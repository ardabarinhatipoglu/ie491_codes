import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from matplotlib.pyplot import *
import math
import docplex
from docplex import mp
from docplex.mp.model import Model
from time import process_time
from scipy.signal import detrend
import matplotlib.ticker as mticker

"""
1. votuporanga - agua vermelha
2. presindente figuereido - balbina
3. uberlandia - miranda
4. estreito
5. itumbiara
6. apiacas - teles pires
7. tucurui
8. planalto - salto caxias
9. catalao - emborcaçao
10. porto velho - santo antonio
https://www.google.com/maps/d/u/0/edit?mid=1xG-lw0W-zprovr5vVjZFRpHWYOpOmiA&usp=sharing
"""

df_wind = pd.read_csv(r"C:\Users\Dell\Desktop\490\weather_sum_all.csv")

df_wind.drop(columns=["rain_max", "rad_max", "temp_avg", "temp_max", "temp_min", "hum_max", "hum_min", "wind_max"],
             inplace=True)

df_wind["date"] = pd.to_datetime(df_wind["DATA (YYYY-MM-DD)"])

df_wind["year"] = df_wind["date"].dt.year
df_wind["month"] = df_wind["date"].dt.month
df_wind["day"] = df_wind["date"].dt.day

df_wind = (
    df_wind.groupby(["ESTACAO", "year", "month", "day"])["wind_avg"]
    .mean()
    .reset_index()
)

df_wind["date"] = pd.to_datetime(df_wind[["year", "month", "day"]])

df_wind = df_wind[
    (df_wind["year"] == 2009)
]

itumbiara = df_wind["ESTACAO"] == "A035"
df_wind_itumbiara = df_wind[itumbiara]

catalao = df_wind["ESTACAO"] == "A034"
df_wind_catalao = df_wind[catalao]

pf = df_wind["ESTACAO"] == "A126"
df_wind_pf = df_wind[pf]

uberlandia = df_wind["ESTACAO"] == "A507"
df_wind_uberlandia = df_wind[uberlandia]

estreito = df_wind["ESTACAO"] == "A224"
df_wind_estrieto = df_wind[estreito]

apiacas = df_wind["ESTACAO"] == "A910"
df_wind_apiacas = df_wind[apiacas]

tucurui = df_wind["ESTACAO"] == "A229"
df_wind_tucurui = df_wind[tucurui]

planalto = df_wind["ESTACAO"] == "A855"
df_wind_planalto = df_wind[planalto]

pv = df_wind["ESTACAO"] == "A925"
df_wind_pv = df_wind[pv]

votuporanga = df_wind["ESTACAO"] == "A729"
df_wind_votuporanga = df_wind[votuporanga]

# print(df_wind.head(20))
# print(f"Total rows: {len(df_wind)}")
# print(f"Columns: {df_wind.columns.tolist()}")
# print(f"Sample station: {df_wind[df_wind['ESTACAO'] == 'A035'].head(10)}")

stations = ["A126", "A729", "A507", "A224", "A035", "A910", "A229", "A855", "A034", "A925"]

# for s in stations:
#    count = len(df_wind[df_wind["ESTACAO"] == s])
#    print(f"{s}: {count} days")
# print(np.sum(df_wind_pv.isna())) = 34
# print(np.sum(df_wind_ss.isna())) = 22
# print(np.sum(df_wind_tucurui.isna())) = 1

df_stream = pd.read_csv(r"C:\Users\Dell\Desktop\490\dailystreamflows.csv")

month_map_pt = {
    "jan": "01", "fev": "02", "mar": "03", "abr": "04",
    "mai": "05", "jun": "06", "jul": "07", "ago": "08",
    "set": "09", "out": "10", "nov": "11", "dez": "12"
}

df_stream["date_fixed"] = df_stream["dates"].str.lower().replace(
    month_map_pt, regex=True
)

df_stream["date"] = pd.to_datetime(df_stream["date_fixed"], format="%d/%m/%Y")

mask = df_stream["date"].dt.year == 2009
df_stream = df_stream[mask]
# print(df_stream.head())

# df_stream = df_stream[
#    (df_stream["year"] == 2000)
# ]

# df_stream.drop(columns=["min", "jan-dec", "max"], inplace=True)

# df_stream = df_stream.melt(
#    id_vars=["dam","year"],
#    value_vars=["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"],
#    var_name="month_str",
#    value_name="streamflow"
# )

# month_map = {
#    "jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
#    "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12
# }
# df_stream["month"] = df_stream["month_str"].map(month_map)
#
# df_stream = df_stream.drop(columns="month_str")

# df_stream = df_stream[["dam","year","month","streamflow"]]
# df_stream = df_stream.sort_values(["dam", "year", "month"]).reset_index(drop=True)

df_stream_av = df_stream[["date", "A. VERMELHA (18)"]].copy()
df_stream_av.columns = ["date", "streamflow"]

df_stream_balb = df_stream[["date", "BALBINA (269)"]].copy()
df_stream_balb.columns = ["date", "streamflow"]

df_stream_mir = df_stream[["date", "MIRANDA (206)"]].copy()
df_stream_mir.columns = ["date", "streamflow"]

df_stream_est = df_stream[["date", "ESTREITO (8)"]].copy()
df_stream_est.columns = ["date", "streamflow"]

df_stream_itum = df_stream[["date", "ITUMBIARA (31)"]].copy()
df_stream_itum.columns = ["date", "streamflow"]

df_stream_tuc = df_stream[["date", "TUCURUI (275)"]].copy()
df_stream_tuc.columns = ["date", "streamflow"]

df_stream_tp = df_stream[["date", "TELES PIRES (229)"]].copy()
df_stream_tp.columns = ["date", "streamflow"]

df_stream_sc = df_stream[["date", "SALTO CAXIAS (222)"]].copy()
df_stream_sc.columns = ["date", "streamflow"]

df_stream_embo = df_stream[["date", "EMBORCACAO (24)"]].copy()
df_stream_embo.columns = ["date", "streamflow"]

df_stream_sa = df_stream[["date", "SANTO ANTONIO (MADEIRA) (287)"]].copy()
df_stream_sa.columns = ["date", "streamflow"]

# print(df_wind_apiacas)
# print(df_stream_tp)
# print(np.sum(df_wind_pf[pf_shape].isna()))
# print(df_wind_pf[pf_shape])
# print(df_stream_balb[balb_shape])
# pearson_1 = df_wind_votuporanga.corr(df_stream_av, method="pearson")
# print(pearson_1)

mergers = []

df_merge_1 = pd.merge(df_wind_pf, df_stream_balb, on=["date"], how="inner")
mergers.append(df_merge_1)

df_merge_2 = pd.merge(df_wind_votuporanga, df_stream_av, on=["date"], how="inner")
mergers.append(df_merge_2)

df_merge_3 = pd.merge(df_wind_uberlandia, df_stream_mir, on=["date"], how="inner")
mergers.append(df_merge_3)

df_merge_4 = pd.merge(df_wind_estrieto, df_stream_est, on=["date"], how="inner")
mergers.append(df_merge_4)

df_merge_5 = pd.merge(df_wind_itumbiara, df_stream_itum, on=["date"], how="inner")
mergers.append(df_merge_5)

df_merge_6 = pd.merge(df_wind_apiacas, df_stream_tp, on=["date"], how="inner")
mergers.append(df_merge_6)

df_merge_7 = pd.merge(df_wind_tucurui, df_stream_tuc, on=["date"], how="inner")
mergers.append(df_merge_7)

df_merge_8 = pd.merge(df_wind_planalto, df_stream_sc, on=["date"], how="inner")
mergers.append(df_merge_8)

df_merge_9 = pd.merge(df_wind_catalao, df_stream_embo, on=["date"], how="inner")
mergers.append(df_merge_9)

df_merge_10 = pd.merge(df_wind_pv, df_stream_sa, on=["date"], how="inner")
mergers.append(df_merge_10)

# for i in mergers:
#    #i["wind_avg"] *= (np.average(df_merge_9["wind_avg"])/np.average(i["wind_avg"]))
#    print(np.sum(i["wind_avg"]))
#    print(f"wind length: {len(i["wind_avg"])} - streamflow length: {len(i["streamflow"])}")
# for i in mergers:
#    print(np.sum(np.isnan((i["wind_avg"]))))
#    print(np.average(i["wind_avg"]))

# print(df_merge_10["wind_avg"])


# print(df_wind_ss)
# print(df_stream_ss)
# print(df_merge_2)

spearmans = []
pearsons = []
obj_values = [3422977979.294359, 2565406919.3853416, 2572479977.7695217, 2663243720.601229, 2621643146.5573597,
              2951113540.8022213, 3271211871.866947, 3325688204.7867575, 2649845271.9452815, 2827257194.860062]
k = 0


# for i in mergers:
#
#    i = i.dropna()
#
#    pearson_coef, pearson_p = pearsonr(i["wind_avg"], i["streamflow"])
#    spearman_coef, spearman_p = spearmanr(i["wind_avg"], i["streamflow"])
#
#    #print(i["dam"].unique())
#    print(f"Pearson: {pearson_coef:.3f}, p={pearson_p:.3f}")
#    print(f"Spearman: {spearman_coef:.3f}, p={spearman_p:.3f}")
#    print(obj_values[k])
#    k += 1
#
#    pearsons.append(pearson_coef)
#    spearmans.append(spearman_coef)
#
# labels = [
#    "Pres. Figueiredo/Balbina",
#    "Votuporanga/Agua Vermelha",
#    "Uberlandia/Miranda",
#    "Estreito",
#    "Itumbiara",
#    "Apiacas/Teles Pires",
#    "Tucurui",
#    "Planalto/Salto Caxias",
#    "Catalao/Emborcacao",
#    "Porto Velho/Santo Antonio"
# ]
#
#
# colors = ["blue", "red", "green", "orange", "purple", "brown", "pink", "gray", "cyan", "magenta"]
#
# fig, (ax1, ax2) = subplots(1, 2, figsize=(16, 6))
#
# for i, label in enumerate(labels):
#    ax1.scatter(pearsons[i], obj_values[i], color=colors[i], label=label, s=100)
#
# ax1.axvline(0, color="black", linewidth=0.5)
# ax1.set_xlabel("Pearson")
# ax1.set_ylabel("Objective Value")
# ax1.set_title("Pearson vs Objective Value")
# ax1.legend(fontsize=8)
#
# for i, label in enumerate(labels):
#    ax2.scatter(spearmans[i], obj_values[i], color=colors[i], label=label, s=100)
#
# ax2.axvline(0, color="black", linewidth=0.5)
# ax2.set_xlabel("Spearman")
# ax2.set_ylabel("Objective Value")
# ax2.set_title("Spearman vs Objective Value")
# ax2.legend(fontsize=8)
#
# tight_layout()
# show()

# scaler = StandardScaler()

# print(df_merge_1["streamflow"].to_list())
# print(df_merge_1["wind_avg"])
# for i in mergers:
#    i["streamflow"] = scaler.fit_transform(i[["streamflow"]])
#    i["wind_avg"] = scaler.fit_transform(i[["wind_avg"]])
#
# subplot(5,2,1)
# title(f"Presindente Figuereido (Wind Speed) vs. (Balbina Streamflow)")
# scatter(df_merge_1["wind_avg"], df_merge_1["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# subplot(5,2,2)
# title(f"Votuporanga (Wind Speed) vs. (Agua Vermelho Streamflow)")
# scatter(df_merge_2["wind_avg"], df_merge_2["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# subplot(5,2,3)
# title(f"Uberlandia (Wind Speed) vs. (Miranda Streamflow)")
# scatter(df_merge_3["wind_avg"], df_merge_3["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# subplot(5,2,4)
# title(f"Estreito (Wind Speed) vs. Estreito (Streamflow)")
# scatter(df_merge_4["wind_avg"], df_merge_4["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# subplot(5,2,5)
# title(f"Itumbiara (Wind Speed) vs. Itumbiara (Streamflow)")
# scatter(df_merge_5["wind_avg"], df_merge_5["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# subplot(5,2,6)
# title(f"Apiacas (Wind Speed) vs. Teles Pires (Streamflow)")
# scatter(df_merge_6["wind_avg"], df_merge_6["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# subplot(5,2,7)
# title(f"Tucuri (Wind Speed) vs. Tucurui (Streamflow)")
# scatter(df_merge_7["wind_avg"], df_merge_7["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# subplot(5,2,8)
# title(f"Planalto (Wind Speed) vs Salto Caxias (Streamflow)")
# scatter(df_merge_8["wind_avg"], df_merge_8["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# subplot(5,2,9)
# title(f"Catalao (Wind Speed) vs. Emborcaçao (Streamflow)")
# scatter(df_merge_9["wind_avg"], df_merge_9["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# subplot(5,2,10)
# title(f"Porto Velho (Wind Speed) vs. Santo Antonio (Streamflow)")
# scatter(df_merge_10["wind_avg"], df_merge_10["streamflow"], s=10)
# xlim(-3, 7)
# ylim(-2, 4)
#
# show()

# fig, ax = subplots(figsize=(14, 6))
#
# ax.plot(df_stream_av["date"], df_stream_av["streamflow"], label="Agua Vermelha")
# ax.plot(df_stream_balb["date"], df_stream_balb["streamflow"], label="Balbina")
##ax.plot(df_stream_mir["date"], df_stream_mir["streamflow"], label="Miranda")
##ax.plot(df_stream_est["date"], df_stream_est["streamflow"], label="Estreito")
##ax.plot(df_stream_itum["date"], df_stream_itum["streamflow"], label="Itumbiara")
##ax.plot(df_stream_tp["date"], df_stream_tp["streamflow"], label="Teles Pires")
# ax.plot(df_stream_tuc["date"], df_stream_tuc["streamflow"], label="Tucurui")
# ax.plot(df_stream_sc["date"], df_stream_sc["streamflow"], label="Salto Caxias")
##ax.plot(df_stream_embo["date"], df_stream_embo["streamflow"], label="Emborcacao")
# ax.plot(df_stream_sa["date"], df_stream_sa["streamflow"], label="Santo Antonio")
#
# ax.set_xlabel("Date")
# ax.set_ylabel("Streamflow (m$^3$/s)")
# ax.set_title("Streamflow by Location")
# ax.legend()
#
# tight_layout()
# show()

# fig, ax = subplots(figsize=(14, 6))
#
# ax.plot(df_wind_votuporanga["date"], df_wind_votuporanga["wind_avg"], label="Votuporanga")
# ax.plot(df_wind_pf["date"], df_wind_pf["wind_avg"], label="Presidente Figueiredo")
# ax.plot(df_wind_uberlandia["date"], df_wind_uberlandia["wind_avg"], label="Uberlandia")
# ax.plot(df_wind_estrieto["date"], df_wind_estrieto["wind_avg"], label="Estreito")
# ax.plot(df_wind_itumbiara["date"], df_wind_itumbiara["wind_avg"], label="Itumbiara")
# ax.plot(df_wind_apiacas["date"], df_wind_apiacas["wind_avg"], label="Apiacas")
# ax.plot(df_wind_tucurui["date"], df_wind_tucurui["wind_avg"], label="Tucurui")
# ax.plot(df_wind_planalto["date"], df_wind_planalto["wind_avg"], label="Planalto")
# ax.plot(df_wind_catalao["date"], df_wind_catalao["wind_avg"], label="Catalao")
# ax.plot(df_wind_pv["date"], df_wind_pv["wind_avg"], label="Porto Velho")
#
# ax.set_xlabel("Date")
# ax.set_ylabel("Wind Speed (m/s)")
# ax.set_title("Wind Speed by Location")
# ax.legend()
#
# tight_layout()
# show()
# for name, df in [("Agua Vermelha", df_stream_av), ("Balbina", df_stream_balb), ("Tucurui", df_stream_tuc)]:
#    print(f"{name}: min={df['streamflow'].min()}, max={df['streamflow'].max()}, avg={df['streamflow'].mean():.1f}")

# fig, ax = subplots(figsize=(8, 8))
#
# labels = [
#    "Pres. Figueiredo/Balbina",
#    "Votuporanga/Agua Vermelha",
#    "Uberlandia/Miranda",
#    "Estreito",
#    "Itumbiara",
#    "Apiacas/Teles Pires",
#    "Tucurui",
#    "Planalto/Salto Caxias",
#    "Catalao/Emborcacao",
#    "Porto Velho/Santo Antonio"
# ]
#
# colors = ["blue", "red", "green", "orange", "purple", "brown", "pink", "gray", "cyan", "magenta"]
#
# for i, label in enumerate(labels):
#    ax.scatter(pearsons[i], spearmans[i], color=colors[i], label=label, s=100)
#
# ax.axhline(0, color="black", linewidth=0.5)
# ax.axvline(0, color="black", linewidth=0.5)
#
# ax.set_xlabel("Pearson")
# ax.set_ylabel("Spearman")
# ax.set_title("Pearson vs Spearman Correlation Coefficients")
# ax.set_xlim(-0.75, 0.75)
# ax.set_ylim(-0.75, 0.75)
# ax.legend(fontsize=8)
#
# tight_layout()
# show()

def get_wind_energy(wind_speed: float) -> float:
    """ Transforms wind speed w_t (in m/s) to wind energy (in kW) """

    # production_curve_int = [0.0, 0.0, 0.0, 0.0, 0.043, 0.131, 0.25, 0.416, 0.64, 0.924, 1.181, 1.359, 1.436, 1.481,
    #                    1.494, 1.5]
    production_curve = [0.0, 22.0, 104.0, 260.0, 523.0, 920.0, 1471.0, 2151.0, 2867.0,
                        3481.0, 3903.0, 4119.0, 4196.0, 4200.0, 4200.0, 4200.0, 4200.0,
                        4200.0, 4200.0, 4200.0, 4200.0, 4200.0, 4200.0, 4200.0, 4200.0]

    # in GW, for wind speed between 0 and 15

    # print(production_curve)

    if wind_speed > 15:
        wind_energy = production_curve[-1]
    else:
        wind_ceil = math.ceil(wind_speed)
        wind_floor = math.floor(wind_speed)
        # interpolation
        wind_energy = (wind_speed - wind_floor) * production_curve[wind_floor] + \
                      (wind_ceil - wind_speed) * production_curve[wind_ceil]
        wind_energy *= 1.5  # estimated speed at 159 m

    return wind_energy


# for i in df_wind_apiacas["wind_avg"]:
#    i = get_wind_energy(i, number_turbines=1)


# df_wind_apiacas["wind_energy"] = df_wind_apiacas["wind_avg"].apply(get_wind_energy)
#
# print(df_wind_apiacas["wind_energy"])

stream_dfs = [
    df_stream_av, df_stream_balb, df_stream_mir, df_stream_est,
    df_stream_itum, df_stream_tp, df_stream_tuc, df_stream_sc,
    df_stream_embo, df_stream_sa
]

for i in mergers:
    i["wind_energy"] = i["wind_avg"].apply(get_wind_energy)

max_avg = max(df["wind_energy"].mean() for df in mergers)
for i in mergers:
    i["wind_energy"] = (i["wind_energy"] / np.average(i["wind_energy"])) * max_avg
    # print(np.average(i["wind_energy"]))

volume_averages = []
for df in mergers:
    df["volume"] = df["streamflow"] * 24 * 60 * 60
    volume_averages.append(np.average(df["volume"]))

# print(volume_averages)

for df in mergers:
    df["volume"] = (df["volume"] / np.average(df["volume"])) * np.average(volume_averages)
    # print(np.average(df["volume"]))

sp = []


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


# plot(periods, merge["volume"])

# show()


# for i in mergers:
# print(np.average(i["wind_energy"]))
# print(np.average(i["wind_avg"]))
# print(max(i["wind_energy"]))
# print(max(i["wind_avg"]))
##thefunc(i)
#    print(np.average(i["volume"]))

# data_path = r"C:\Users\Dell\Desktop\data (1).xlsx"
# df_demand = pd.read_excel(data_path, sheet_name="demand", header=None)
# demand_list = df_demand.iloc[:,6].tolist()
# print(demand_list)
# print(sum(demand_list))

mergers5 = [df_merge_1, df_merge_2, df_merge_7, df_merge_8, df_merge_10]

# thefunc(df_merge_2)

# for i, m in enumerate(mergers5):
#    subplot(5,1,i+1)
#    plot(range(len(m)), demand_list[:len(m)])
#    plot(range(len(m)), m["wind_energy"]*10)
#    plot(range(len(m)), m["volume"]/1000)
# show()

# for m in mergers5:
#    thefunc(m)

thefunc(df_merge_8)

# print(np.average(df_merge_10["wind_avg"]))

# sf_clean = {}
# wind_clean = {}
# for i in mergers5:
#    sf_clean[i] = detrend(i["volume"].tolist())    # removes linear trend only
#    wind_clean[i] = detrend(i["wind_avg"])

# Then normalize

# sf_clean = (df_merge_8["volume"] - df_merge_8["volume"].mean()) / df_merge_8["volume"].std()
# wind_clean = (df_merge_8["wind_avg"] - df_merge_8["wind_avg"].mean()) / df_merge_8["wind_avg"].std()
#
# s0 = 2
# s_max = 60
#
# J = int(np.log2(s_max / s0) / (1/12))
# scales = s0 * 2 ** (np.arange(J) * (1/12))
#
## Day-to-day changes
# dsf   = pd.Series(sf_clean).diff()
# dwind = pd.Series(wind_clean).diff()
#
## Same direction = 1, opposite = -1
# concordance = np.sign(dsf) * np.sign(dwind)
#
## Rolling co-movement rate (e.g., over 2-week windows)
# rolling_concord = concordance.rolling(14, center=True).mean()
#
# figure(figsize=(12, 4))
# plot(rolling_concord, color='steelblue', lw=1.5)
# axhline(0, color='k', lw=0.8, linestyle='--')
# fill_between(range(len(rolling_concord)), rolling_concord, where=rolling_concord > 0, color='green', alpha=0.3, label='Co-moving')
# fill_between(range(len(rolling_concord)), rolling_concord, where=rolling_concord < 0, color='red', alpha=0.3, label='Opposing')
# legend()
# title('Rolling directional co-movement (14-day window)')
# ylabel('Co-movement index (−1 to +1)')
# show()
#

# import pandas as pd
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.ticker as mticker
#
## ── load & parse ──────────────────────────────────────────────────────────────
# df_stream = pd.read_csv(r"C:\Users\Dell\Desktop\490\dailystreamflows.csv")
#
# month_map_pt = {
#    "jan": "01", "fev": "02", "mar": "03", "abr": "04",
#    "mai": "05", "jun": "06", "jul": "07", "ago": "08",
#    "set": "09", "out": "10", "nov": "11", "dez": "12"
# }
# df_stream["date_fixed"] = df_stream["dates"].str.lower().replace(month_map_pt, regex=True)
# df_stream["date"] = pd.to_datetime(df_stream["date_fixed"], format="%d/%m/%Y")
# df_stream = df_stream[df_stream["date"].dt.year == 2009]
#
## ── pick three sites ──────────────────────────────────────────────────────────
# sites = {
#    "Agua Vermelha": "A. VERMELHA (18)",
#    "Salto Caxias":  "SALTO CAXIAS (222)",
#    "Santo Antonio": "SANTO ANTONIO (MADEIRA) (287)",
# }
# colors = {
#    "Agua Vermelha": "#378ADD",
#    "Salto Caxias":  "#3B6D11",
#    "Santo Antonio": "#D85A30",
# }
#
# dfs = {}
# for name, col in sites.items():
#    tmp = df_stream[["date", col]].copy()
#    tmp.columns = ["date", "streamflow"]
#    dfs[name] = tmp
#
## ── scale (same logic as main script) ────────────────────────────────────────
# for name in dfs:
#    dfs[name]["volume"] = dfs[name]["streamflow"] * 86400
#
# vol_means   = {name: dfs[name]["volume"].mean() for name in dfs}
# global_mean = np.mean(list(vol_means.values()))
#
# scaled = {}
# for name in dfs:
#    scaled[name] = dfs[name]["streamflow"] * (global_mean / vol_means[name])
#
# shared_mean = np.mean([scaled[n].mean() for n in scaled])
#
## ── plot ──────────────────────────────────────────────────────────────────────
# fig, (ax1, ax2) = subplots(2, 1, figsize=(13, 8), sharex=True)
# fig.patch.set_facecolor("white")
#
# def style_ax(ax):
#    ax.set_facecolor("white")
#    ax.spines[["top", "right"]].set_visible(False)
#    ax.spines[["left", "bottom"]].set_color("#dddddd")
#    ax.yaxis.grid(True, color="#eeeeee", linewidth=0.8, zorder=0)
#    ax.set_axisbelow(True)
#    ax.tick_params(colors="#888888", labelsize=10)
#    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
#
## — before —
# for name in dfs:
#    s = dfs[name]["streamflow"]
#    ax1.plot(dfs[name]["date"], s, color=colors[name], linewidth=1.2, label=name, zorder=2)
#    ax1.axhline(s.mean(), color=colors[name], linewidth=1.0, linestyle="--",
#                alpha=0.7, zorder=3, label=f"{name} mean ({s.mean():,.0f} m³/s)")
#
# ax1.set_title("Before scaling — raw daily streamflow", fontsize=12, color="#333333", pad=10)
# ax1.set_ylabel("Streamflow (m³/s)", fontsize=10, color="#666666")
# style_ax(ax1)
# ax1.legend(fontsize=8, frameon=False, ncol=2, labelcolor="#444444")
#
## — after —
# for name in dfs:
#    ax2.plot(dfs[name]["date"], scaled[name], color=colors[name], linewidth=1.2, label=name, zorder=2)
#
# ax2.axhline(shared_mean, color="#888888", linewidth=1.0, linestyle="--",
#            alpha=0.7, zorder=3, label=f"shared mean ({shared_mean:,.0f} m³/s)")
#
# ax2.set_title("After scaling — volumes normalised to common average", fontsize=12, color="#333333", pad=10)
# ax2.set_ylabel("Streamflow (m³/s)", fontsize=10, color="#666666")
# ax2.set_xlabel("Date", fontsize=10, color="#666666")
# style_ax(ax2)
# ax2.legend(fontsize=8, frameon=False, ncol=2, labelcolor="#444444")
#
# tight_layout()
# savefig("streamflow_before_after.png", dpi=150, bbox_inches="tight")
# show()