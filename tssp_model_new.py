import pandas as pd
import numpy as np
from matplotlib import *

def thefunc(merge):
    # params
    l = 0.05
    g = 9.81
    h_U = 100
    h_L = 100
    C_H = 3
    C_PG = 500
    C_S = 200
    C_W = 1100000
    # c_T = 1100000
    C_T = 1.1
    dist = 50
    alpha = 0.88
    M = 1000000000
    gamma = 0.12
    # num = 3.6e9

    # print(periods)
    d = 1000
    # num_gens = 1

    periods = range(len(merge))

    mu = 0.25
    T = periods[-1]

    data_path = r"C:\Users\Dell\Desktop\data (1).xlsx"
    df_wind = pd.read_excel(data_path, sheet_name="wind", header=None)
    wind_list = merge["wind_energy"]

    df_hydro = pd.read_excel(data_path, sheet_name="hydro", header=None)
    hydro_list = merge["volume"]

    df_demand = pd.read_excel(data_path, sheet_name="demand", header=None)
    demand_list = df_demand.iloc[:, 6].tolist()
    # print(demand_list)
    # print(sum(demand_list))
    demand_list = demand_list[0:len(merge)]
    demand_list = [i * 24 * 7 for i in demand_list]
    merge["demand_list"] = demand_list
    # print(sum(demand_list))

    d_h = 0.05 / (1 - pow(1.05, -60))
    d_g = 0.05 / (1 - pow(1.05, -30))
    d_i = 0.05 / (1 - pow(1.05, -40))
    d_w = 0.05 / (1 - pow(1.05, -20))
    # d_s = 0.05/(1-pow(1.05,-30))

    t1_start = process_time()
    m = Model()

    stored_U_max = m.continuous_var(name="upper reservoir cap", lb=0)
    stored_L_max = m.continuous_var(name="lower reservoir cap", lb=0)
    PG_U_max = m.continuous_var(name="upper generator cap", lb=0)
    PG_L_max = m.continuous_var(name="lower generator cap", lb=0)
    T_max = m.continuous_var(name="transmission line cap", lb=0)
    # Area = m.continuous_var(name="solar panel area", lb=0)
    turbine_num = m.integer_var(name="number of wind turbines", lb=0)

    stored_L = m.continuous_var_list(periods, name="water stored in lower reservoir", lb=0)
    stored_U = m.continuous_var_list(periods, name="water stored in upper reservoir", lb=0)
    pumped = m.continuous_var_list(periods, name="water pumped to upper reservoir", lb=0)
    release_U = m.continuous_var_list(periods, name="water released from upper reservoir", lb=0)
    release_L = m.continuous_var_list(periods, name="water released from lower reservoir", lb=0)
    used_wind = m.continuous_var_list(periods, name="wind energy directly used in the demand points", lb=0)
    misdemand = m.continuous_var_list(periods, name="mismatched demand", lb=0)
    spill_U = m.continuous_var_list(periods, name="water spilled from upper reservoir", lb=0)
    spill_L = m.continuous_var_list(periods, name="water spilled from lower reservoir", lb=0)
    curtailed = m.continuous_var_list(periods, name="curtailed renewable energy", lb=0)
    total_prod = m.continuous_var_list(periods, name="total production", lb=0)
    power_gen = m.continuous_var_list(periods, name="power generated", lb=0)
    power_pumped = m.continuous_var_list(periods, name="power used for pumping", lb=0)
    capex = m.continuous_var(lb=0)
    opex_pen = m.continuous_var(lb=0)
    opex_eps = m.continuous_var(lb=0)
    binary_pump = m.binary_var_list(periods)

    # for o in scenarios:
    #    inflows = hydro_list[o]
    # wind_prof = wind_list[o % len(wind_list)]
    # for t in periods:
    #    power_gen1 = pumped[t,o]*d*g*h_U*alpha/num
    #    power_pumped1 = pumped[t,o]*d*g*h_U/(alpha*num)

    # material balance
    # m.add_constraints(stored_U[t] == stored_U[t-1] + hydro_list[t] - release_U[t] - spill_U[t] for t in periods)
    m.add_constraints(
        stored_U[t] == stored_U[t - 1] + hydro_list[t] - release_U[t] - spill_U[t] + pumped[t] for t in periods)
    m.add_constraints(stored_L[t] == stored_L[t - 1] - pumped[t] + release_U[t] - spill_L[t] for t in periods)

    # initial conditions
    m.add_constraint(stored_U[0] == stored_U_max / 2 + hydro_list[0] - release_U[0] - spill_U[0] + pumped[0])
    # m.add_constraint(stored_U[0] == stored_U_max/2 + hydro_list[0] - release_U[0] - spill_U[0])
    m.add_constraint(stored_L[0] == stored_L_max / 2 - pumped[0] + release_U[0] - spill_L[0])

    # final conditions
    m.add_constraint(stored_U[T] == stored_U_max / 2)
    m.add_constraint(stored_L[T] == stored_L_max / 2)

    # maximum capacity for res
    m.add_constraints(stored_U[t] <= stored_U_max for t in periods)
    m.add_constraints(stored_L[t] <= stored_L_max for t in periods)

    # meet demand?
    m.add_constraints(
        demand_list[t] == misdemand[t] + used_wind[t] + release_U[t] * g * h_U * alpha * (1 - l) * d / (3.6e6) for t in
        periods)
    # m.add_constraints(demand_list[t] == misdemand[t] + used_wind[t] + release_U[t]*g*h_U*alpha*(1-l)*d/(3.6e6) for t in periods)

    # generator cap
    m.add_constraints(release_U[t] * g * h_U * alpha * d / (3.6e6 * 24) <= PG_U_max for t in periods)
    m.add_constraints(power_pumped[t] <= PG_U_max for t in periods)
    # m.add_constraints(release_L[t]*g*h_U*alpha*d/(3.6e6*24) <= PG_L_max for t in periods)

    # iletim
    m.add_constraints(release_U[t] * g * h_U * alpha * d / (3.6e6 * 24) <= T_max for t in periods)
    # m.add_constraints(release_U[t]*g*h_U*alpha*d/(3.6e6*24)<= T_max for t in periods)
    m.add_constraints(power_pumped[t] / (1 - l) <= T_max for t in periods)

    # m.add_constraints(used_solar[t,o] + curtailed[t,o] == Area*gamma*solar_list[t] for t in periods for o in scenarios)

    # m.add_constraints(used_wind[t] + curtailed[t] == turbine_num*wind_list[t]*24 for t in periods)
    m.add_constraints(
        used_wind[t] + curtailed[t] + power_pumped[t] / (1 - l) == turbine_num * wind_list[t] * 24 for t in periods)

    # m.add_constraint(turbine_num >= 2875)

    # pump hacim-enerji
    m.add_constraints(power_pumped[t] == pumped[t] * g * h_U * d / (alpha * 3.6e6) for t in periods)

    # binary constraints
    m.add_constraints(pumped[t] <= binary_pump[t] * M for t in periods)
    m.add_constraints(release_U[t] <= (1 - binary_pump[t]) * M for t in periods)
    # m.add_constraints(release_L[t] <= (1-binary_pump[t])*M for t in periods)

    m.minimize(
        (d_h * C_H * (stored_U_max + stored_L_max)) +
        (d_g * C_PG * (PG_U_max + PG_L_max)) +
        (d_w * C_W * turbine_num) +
        (d_i * C_T * (T_max / 1e6) * dist) +
        mu * sum(misdemand[t] for t in periods))

    # m.parameters.lpmethod = 1
    # print("[INFO] Solving (Barrier)...")
    # m.parameters.barrier.convergetol = 1e-9
    # m.parameters.barrier.display = 2
    # m.parameters.barrier.crossover = 1
    # m.parameters.mip.tolerances.mipgap = 1e-6
    # m.parameters.mip.tolerances.integrality = 1e-6
    # m.parameters.emphasis.numerical = 1
    # m.parameters.timelimit = 3600
    # print(docplex.__version__)

    m.solve(log_output=True)
    t1_stop = process_time()

    if m.solution:
        # --- DEĞERLERİN HESAPLANMASI ---

        # 1. Kapasiteler
        val_Smax_km3 = stored_U_max.solution_value
        val_Saltmax_km3 = stored_L_max.solution_value / 1e9
        val_PJmax_GW = PG_U_max.solution_value
        val_Lower_Gen_GW = 0.0  # Semi-Open modelde alt rezervuar jeneratörü yoktur
        val_N = turbine_num.solution_value
        val_Imax_GW = T_max.solution_value
        val_Obj = capex.solution_value + opex_eps.solution_value + opex_pen.solution_value

        # 2. Enerji Ortalamaları (Tüm senaryolar üzerinden)
        avg_solar_used = sum(used_wind[t].solution_value for t in periods)
        avg_pump_energy = sum(pumped[t].solution_value for t in periods) * (d * g * h_U) / (alpha * (1 - l) * 3.6e6)
        avg_solar_curtailed = sum(curtailed[t].solution_value for t in periods)

        # Hydro Upper: Üretilen Hidroelektrik
        avg_hydro_upper = sum(release_U[t].solution_value for t in periods) * d * g * h_U * alpha * (1 - l) / (3.6e6)
        # Hydro Lower: Semi-Open modelde 0'dır
        avg_hydro_lower = sum(release_L[t].solution_value for t in periods) * d * g * h_U * alpha * (1 - l) / (3.6e6)

        total_demand = sum(demand_list[t] for t in periods)
        avg_shortage = sum(misdemand[t].solution_value for t in periods)
        total_consumption = avg_hydro_upper + avg_shortage + avg_solar_used + avg_hydro_lower

        hydro_power = [(release_U[t].solution_value) * d * g * h_U * alpha * (1 - l) / (3.6e6) for t in periods]

        pumpmax = max([pumped[t].solution_value for t in periods])
        releasemax = max([release_U[t].solution_value for t in periods])

        cost_reservoir = d_h * C_H * stored_U_max.solution_value
        cost_generator = d_g * C_PG * PG_U_max.solution_value
        cost_wind = d_w * C_W * turbine_num.solution_value
        cost_trans = d_i * C_T * (T_max / 1e6).solution_value * dist
        cost_penalty = mu * avg_shortage

        if total_consumption > 0:
            lcoe = m.objective_value / (total_consumption)
        else:
            lcoe = 0

        # --- EKRAN ÇIKTISI (Kısa Özet) ---
        print(f"Objective ($)                 : {m.objective_value}")
        print(f"N                             : {val_N}")
        print(f"LCOE ($/kWh)                  : {lcoe}")
        print(f"Total Cons. (GWh)             : {total_consumption / 1e6}")
        print(f"Upper reservoir max cap (m3)  : {stored_U_max.solution_value}")
        print(f"Lower reservoir max cap (m3)  : {stored_L_max.solution_value}")
        print(f"Upper Generator Cap (GW)      : {PG_U_max.solution_value / 1e6}")
        print(f"Lower Generator Cap (GW)      : {PG_L_max.solution_value / 1e6}")
        print(f"Transmission Cap (GW)         : {T_max.solution_value / 1e6}")
        print(f"Shortage (GWh)                : {avg_shortage / 1e6}")
        print(f"Hydro upper prod. (GWh)       : {avg_hydro_upper / 1e6}")
        print(f"Hydro lower prod. (GWh)       : {avg_hydro_lower / 1e6}")
        print(f"Wind used for demand (GWh)    : {avg_solar_used / 1e6}")
        print(f"Wind curtailed (GWh)          : {avg_solar_curtailed / 1e6}\n")
        print(f"Reservoir cost: ${cost_reservoir:,.0f} ({100 * cost_reservoir / m.objective_value:.1f}%)")
        print(f"Generator cost: ${cost_generator:,.0f} ({100 * cost_generator / m.objective_value:.1f}%)")
        print(f"Wind cost:      ${cost_wind:,.0f} ({100 * cost_wind / m.objective_value:.1f}%)")
        print(f"Transmission:   ${cost_trans:,.0f} ({100 * cost_trans / m.objective_value:.1f}%)")
        print(f"Penalty cost:   ${cost_penalty:,.0f} ({100 * cost_penalty / m.objective_value:.1f}%)")
        try:
            print(f"Reservoir cost per kWh hydro: ($/kWh) {cost_reservoir / avg_hydro_upper}")
        except:
            print(f"Reservoir cost per kWh hydro: ($/kWh) NA")
        try:
            print(f"Wind cost per kWh wind: ($/kWh) {cost_wind / avg_solar_used}")
        except:
            print(f"Wind cost per kWh wind: ($/kWh) NA")
        print(f"MD cost per kWh MD: ($/kWh) {cost_penalty / avg_shortage}")
        try:
            print(f"Total hydro cost per kWh hydro: ($/kWh) {(cost_reservoir + cost_generator) / avg_hydro_upper}\n")
        except:
            print(f"Total hydro cost per kWh hydro: ($/kWh) NA")
        print(f"Max streamflow (m^3):{max(hydro_list[t] for t in periods)}")
        print(f"Max wind energy (kWh):{max(wind_list[t] for t in periods)}")
        print(f"Total pumped energy (kWh): {avg_pump_energy}\n")
        print(pumpmax)
        print(releasemax)
        # plot(periods, merge["volume"])

        # title("Demand vs. Wind Energy vs. Hydro Energy")
        # plot(range(len(merge)), demand_list)
        # plot(range(len(merge)), turbine_num.solution_value*wind_list*24)
        # plot(range(len(merge)), hydro_power)
        # show()
    else:
        print("no solution")

    period_list = list(periods)

    # --- data (convert to GWh) ---
    demand_gwh = [demand_list[t] / 1e6 for t in periods]
    hydro_gwh = [release_U[t].solution_value * d * g * h_U * alpha * (1 - l) / 3.6e12 for t in periods]
    wind_gwh = [turbine_num.solution_value * wind_list[t] * 24 / 1e6 for t in periods]

    fig, ax = subplots(figsize=(14, 5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    hydro_arr = np.array(hydro_gwh)
    wind_arr = np.array(wind_gwh)

    # fill blue only where hydro >= wind
    ax.fill_between(period_list, hydro_arr, wind_arr,
                    where=(hydro_arr >= wind_arr),
                    color="#378ADD", alpha=0.15, zorder=1)

    # fill green only where wind > hydro
    ax.fill_between(period_list, wind_arr, hydro_arr,
                    where=(wind_arr > hydro_arr),
                    color="#3B6D11", alpha=0.15, zorder=1)

    # hydro — ghost line
    ax.plot(period_list, hydro_arr,
            color="#378ADD", linewidth=0.4, alpha=0.25, label="Hydro generation", zorder=2)

    # wind — solid thin line
    ax.plot(period_list, wind_arr,
            color="#3B6D11", linewidth=0.6, label="Wind generation", zorder=2)

    # demand — bold black
    ax.plot(period_list, demand_gwh,
            color="#1a1a1a", linewidth=2, label="Demand", zorder=3)

    # clean up axes
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#dddddd")
    ax.yaxis.grid(True, color="#eeeeee", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(colors="#888888", labelsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f} GWh"))

    ax.set_xlabel("Period", color="#888888", fontsize=11)
    ax.legend(frameon=False, fontsize=10, labelcolor="#444444")

    tight_layout()
    savefig("energy_mix.png", dpi=150, bbox_inches="tight")
    show()
