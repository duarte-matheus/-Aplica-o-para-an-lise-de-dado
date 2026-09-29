import pandas as pd
from app import carregar_transacoes, filtro_setembro_sp_rj, calcular_anomalias

df = carregar_transacoes()

assert "plataforma" in df.columns
assert (df["plataforma"] == "Mobile").all()
assert df["data_transacao"].dt.tz is not None
assert df["valor"].isna().sum() == 0
assert df.duplicated().sum() == 0

filtrado = filtro_setembro_sp_rj(df)
assert (filtrado["mes"] == 9).all()
assert filtrado["estado_cliente"].isin(["SP", "RJ"]).all()
assert (filtrado["valor"] > 5000).all()

anomalias = calcular_anomalias(df)
assert (anomalias["z_score"] > 2.5).all()

print("Todos os testes básicos passaram.")
