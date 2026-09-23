"""
比較 台灣(TAIEX) vs 日本(JPN)、韓國(KOSPI)、印度(IND)
半年報酬率與半年風險(變異數)，2011~2025 共 30 個半年樣本。

資料來源：資產組合(NLP) -更新.xlsx  分頁「歷史資料」 (A:E = Date, KOSPI, TAIEX, JPN, IND 每日指數)
F 檢定：兩個常態母體變異數的檢定 (檢查兩市場的風險是否相等)
t 檢定：兩個母體平均數差的檢定，假設變異數不相等 (Welch t-test，檢查兩市場的報酬是否相等)
每半年報酬率 = 該半年最後交易日指數 / 該半年第一個交易日指數 - 1
"""
import pandas as pd
import numpy as np
from scipy import stats

FILE = "資產組合(NLP) -更新.xlsx"

df = pd.read_excel(FILE, sheet_name="歷史資料", usecols="A:E", header=0)
df.columns = ["Date", "KOSPI", "TAIEX", "JPN", "IND"]
df = df.dropna(subset=["Date"]).sort_values("Date")
df = df[(df.Date.dt.year >= 2011) & (df.Date.dt.year <= 2025)]

half = df.Date.dt.year.astype(str) + "H" + np.where(df.Date.dt.month <= 6, "1", "2")
# 計算半年報酬率
rets = df.groupby(half)[["TAIEX", "JPN", "KOSPI", "IND"]].agg(lambda s: s.iloc[-1] / s.iloc[0] - 1)
rets = rets.sort_index()

# Check: 資料足30期
assert len(rets) == 30, f"預期 30 個半年樣本(2011~2025)，實際取得 {len(rets)} 個"  


def compare(a: pd.Series, b: pd.Series, name_a: str, name_b: str) -> None:
    mean_a, mean_b = a.mean(), b.mean()
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)

    # F 檢定：兩個常態母體變異數的檢定
    F = var_a / var_b if var_a > var_b else var_b / var_a
    dof = len(a) - 1
    p_f = 2 * min(stats.f.sf(F, dof, dof), stats.f.cdf(F, dof, dof))

    # t 檢定：假設變異數不相等 (Welch's t-test)
    t_stat, p_t = stats.ttest_ind(a, b, equal_var=False)

    print(f"\n=== {name_a} vs {name_b} (半年報酬率, n={len(a)}) ===")
    print(f"{name_a:12s} 平均報酬={mean_a:8.2%}  變異數(風險)={var_a:.6f}")
    print(f"{name_b:12s} 平均報酬={mean_b:8.2%}  變異數(風險)={var_b:.6f}")
    print(f"F 檢定 : F={F:.4f}, p={p_f:.4f} -> {'風險有顯著差異' if p_f < 0.05 else '風險無顯著差異'}")
    print(f"t 檢定 : t={t_stat:.4f}, p={p_t:.4f} -> {'報酬有顯著差異' if p_t < 0.05 else '報酬無顯著差異'}")


compare(rets.TAIEX, rets.JPN, "台灣(TAIEX)", "日本(JPN)")
compare(rets.TAIEX, rets.KOSPI, "台灣(TAIEX)", "韓國(KOSPI)")
compare(rets.TAIEX, rets.IND, "台灣(TAIEX)", "印度(IND)")
