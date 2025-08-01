# Aplicação para cálculo de ICMS e outros impostos de multiplos produtos
import streamlit as st
import pandas as pd

# Lista para armazenar produtos adicionados
data = []

# Função para cálculo de importação por item
def calcular_importacao(
    moeda,
    preco_unitario,
    quantidade,
    ii_aliquota,
    ipi_aliquota,
    pis_aliquota,
    cofins_aliquota,
    icms_aliquota,
    comprimento,
    largura,
    altura,
    peso_bruto,
    frete_total
):
    valor_produto_usd = preco_unitario * quantidade
    seguro_usd = valor_produto_usd * 0.0025
    cif_usd = valor_produto_usd + frete_total + seguro_usd

    cif_brl = cif_usd * moeda

    volume_unitario = comprimento * largura * altura
    volume_total = volume_unitario * quantidade
    peso_total = peso_bruto * quantidade
    peso_cubado = volume_total * 167

    afmm = frete_total * 0.25 * moeda
    capatazia = 251.06
    siscomex = 185.00

    ii = cif_brl * ii_aliquota
    ipi = (cif_brl + ii) * ipi_aliquota
    pis = (cif_brl + ii) * pis_aliquota
    cofins = (cif_brl + ii) * cofins_aliquota

    base_icms = cif_brl + ii + ipi + pis + cofins + siscomex + capatazia + afmm
    icms = base_icms * icms_aliquota / (1 - icms_aliquota)

    valor_total = base_icms + icms

    return {
        "Valor Produto (USD)": valor_produto_usd,
        "Seguro (USD)": seguro_usd,
        "CIF (USD)": cif_usd,
        "CIF (BRL)": cif_brl,
        "AFMM (BRL)": afmm,
        "Capatazia (BRL)": capatazia,
        "SISCOMEX (BRL)": siscomex,
        "II (BRL)": ii,
        "IPI (BRL)": ipi,
        "PIS (BRL)": pis,
        "COFINS (BRL)": cofins,
        "ICMS (BRL)": icms,
        "Volume Total (m³)": volume_total,
        "Peso Total (kg)": peso_total,
        "Peso Cubado (kg)": peso_cubado,
        "Valor Total com Impostos (BRL)": valor_total
    }

st.title("Calculadora de Custos de Importação - Multi Produtos")

with st.expander("⚙️ Parâmetros da Importação"):
    moeda = st.number_input("Cotação do Dólar (USD → BRL)", value=5.30)
    ii = st.number_input("Alíquota II (%)", value=12.0) / 100
    ipi = st.number_input("Alíquota IPI (%)", value=10.0) / 100
    pis = st.number_input("Alíquota PIS (%)", value=1.86) / 100
    cofins = st.number_input("Alíquota COFINS (%)", value=8.54) / 100
    icms = st.number_input("Alíquota ICMS (%)", value=18.0) / 100

st.subheader("📦 Adicionar Produto à Importação")

with st.form("form_produto"):
    col1, col2 = st.columns(2)
    with col1:
        ncm = st.text_input("Código NCM")
        descricao = st.text_input("Descrição do Produto")
        preco_unitario = st.number_input("Preço Unitário (USD)", min_value=0.0, step=0.01)
        quantidade = st.number_input("Quantidade", min_value=1)
        frete = st.number_input("Frete (USD)", min_value=0.0, step=0.01)
    with col2:
        comprimento = st.number_input("Comprimento (m)", min_value=0.0, step=0.01)
        largura = st.number_input("Largura (m)", min_value=0.0, step=0.01)
        altura = st.number_input("Altura (m)", min_value=0.0, step=0.01)
        peso_bruto = st.number_input("Peso Bruto (kg)", min_value=0.0, step=0.1)

    adicionar = st.form_submit_button("➕ Adicionar Produto")

if "produtos" not in st.session_state:
    st.session_state.produtos = []

if adicionar:
    calculo = calcular_importacao(
        moeda, preco_unitario, quantidade, ii, ipi, pis, cofins, icms,
        comprimento, largura, altura, peso_bruto, frete
    )
    item = {
        "NCM": ncm,
        "Descrição": descricao,
        "Preço Unitário (USD)": preco_unitario,
        "Quantidade": quantidade,
        **calculo
    }
    st.session_state.produtos.append(item)
    st.success("Produto adicionado com sucesso!")

if st.session_state.produtos:
    st.subheader("📊 Produtos Incluídos")
    df = pd.DataFrame(st.session_state.produtos)
    st.dataframe(df, use_container_width=True)

    total = df[[
        "Valor Produto (USD)", "Seguro (USD)", "CIF (USD)", "CIF (BRL)",
        "AFMM (BRL)", "Capatazia (BRL)", "SISCOMEX (BRL)",
        "II (BRL)", "IPI (BRL)", "PIS (BRL)", "COFINS (BRL)", "ICMS (BRL)",
        "Valor Total com Impostos (BRL)"
    ]].sum().rename("Total Geral")

    st.subheader("📦 Totais da Importação")
    st.dataframe(total.to_frame(), use_container_width=True)

    if st.button("🔁 Limpar Produtos"):
        st.session_state.produtos = []
        st.experimental_rerun()
else:
    st.info("Nenhum produto adicionado ainda.")
