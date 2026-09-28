--[[ ===========================================================================
  interlinear.lua — motor do interlinear (LuaLaTeX)
  Lê arquivos TSV (uma palavra por linha) e escreve macros TeX.
  Colunas reconhecidas (a ordem não importa; a 1ª linha não comentada é o
  cabeçalho): ref, palavra, translit, lema, strong, morf, pt, en, var, freq_nt
  Linhas iniciadas por # são comentários (fonte, licença etc.).
  Convenções nas glosas: [palavra] = termo implícito (sai em cinza).
=========================================================================== ]]
EB = EB or {}
local cache = {}

-- ---------------------------------------------------------------- leitura
local function split_tab(linha)
  local t = {}
  for campo in (linha .. "\t"):gmatch("(.-)\t") do
    t[#t + 1] = campo:gsub("^%s+", ""):gsub("%s+$", "")
  end
  return t
end

local function abrir(caminho)
  local f = io.open(caminho, "r")
  if not f and kpse then
    local achado = kpse.find_file(caminho, "tex")
    if achado then f = io.open(achado, "r") end
  end
  return f
end

function EB.ler(caminho)
  if cache[caminho] then return cache[caminho] end
  local f = abrir(caminho)
  if not f then
    tex.error("Interlinear: arquivo '" .. caminho .. "' não encontrado.")
    return {}
  end
  local cab, linhas = nil, {}
  for linha in f:lines() do
    linha = linha:gsub("\r$", "")
    if linha:match("^%s*#") or linha:match("^%s*$") then
      -- comentário ou linha vazia
    elseif not cab then
      cab = split_tab(linha)
    else
      local campos, reg = split_tab(linha), {}
      for i, nome in ipairs(cab) do reg[nome] = campos[i] or "" end
      local c, v = (reg.ref or ""):match("^(%d+):(%d+)")
      reg.cap, reg.vers = tonumber(c) or 0, tonumber(v) or 0
      reg._i = #linhas + 1
      linhas[#linhas + 1] = reg
    end
  end
  f:close()
  cache[caminho] = linhas
  return linhas
end

local function ref_num(s)
  local c, v = (s or ""):match("^(%d+):(%d+)")
  if c then return tonumber(c) * 1000 + tonumber(v) end
  return nil
end

local function no_intervalo(reg, de, ate)
  local n = reg.cap * 1000 + reg.vers
  local a, b = ref_num(de), ref_num(ate)
  return (not a or n >= a) and (not b or n <= b)
end

-- ------------------------------------------------------ escape para o TeX
local ESC = { ["\\"] = "\\textbackslash{}", ["{"] = "\\{", ["}"] = "\\}",
  ["%"] = "\\%", ["&"] = "\\&", ["#"] = "\\#", ["_"] = "\\_", ["$"] = "\\$",
  ["^"] = "\\^{}", ["~"] = "\\textasciitilde{}" }
local function esc(s)
  s = (s or ""):gsub("[\\{}%%&#_%$%^~]", ESC)
  s = s:gsub("%[(.-)%]", "\\EBimplicito{%1}")
  return s
end

-- --------------------------------------------- transliteração do grego (SBL)
-- gerado a partir de unicodedata (NFD): cp = {base, aspirada, iota_subscrito, diérese, maiúscula}
local D = {
[880]={881,0,0,0,1},[882]={883,0,0,0,1},[886]={887,0,0,0,1},[895]={1011,0,0,0,1},
[902]={945,0,0,0,1},[904]={949,0,0,0,1},[905]={951,0,0,0,1},[906]={953,0,0,0,1},[908]={959,0,0,0,1},
[910]={965,0,0,0,1},[911]={969,0,0,0,1},[912]={953,0,0,1,0},[913]={945,0,0,0,1},[914]={946,0,0,0,1},
[915]={947,0,0,0,1},[916]={948,0,0,0,1},[917]={949,0,0,0,1},[918]={950,0,0,0,1},[919]={951,0,0,0,1},
[920]={952,0,0,0,1},[921]={953,0,0,0,1},[922]={954,0,0,0,1},[923]={955,0,0,0,1},[924]={956,0,0,0,1},
[925]={957,0,0,0,1},[926]={958,0,0,0,1},[927]={959,0,0,0,1},[928]={960,0,0,0,1},[929]={961,0,0,0,1},
[931]={963,0,0,0,1},[932]={964,0,0,0,1},[933]={965,0,0,0,1},[934]={966,0,0,0,1},[935]={967,0,0,0,1},
[936]={968,0,0,0,1},[937]={969,0,0,0,1},[938]={953,0,0,1,1},[939]={965,0,0,1,1},[940]={945,0,0,0,0},
[941]={949,0,0,0,0},[942]={951,0,0,0,0},[943]={953,0,0,0,0},[944]={965,0,0,1,0},[962]={963,0,0,0,0},
[970]={953,0,0,1,0},[971]={965,0,0,1,0},[972]={959,0,0,0,0},[973]={965,0,0,0,0},[974]={969,0,0,0,0},
[984]={985,0,0,0,1},[986]={987,0,0,0,1},[988]={989,0,0,0,1},[990]={991,0,0,0,1},[992]={993,0,0,0,1},
[1015]={1016,0,0,0,1},[1018]={1019,0,0,0,1},[7936]={945,0,0,0,0},[7937]={945,1,0,0,0},
[7938]={945,0,0,0,0},[7939]={945,1,0,0,0},[7940]={945,0,0,0,0},[7941]={945,1,0,0,0},
[7942]={945,0,0,0,0},[7943]={945,1,0,0,0},[7944]={945,0,0,0,1},[7945]={945,1,0,0,1},
[7946]={945,0,0,0,1},[7947]={945,1,0,0,1},[7948]={945,0,0,0,1},[7949]={945,1,0,0,1},
[7950]={945,0,0,0,1},[7951]={945,1,0,0,1},[7952]={949,0,0,0,0},[7953]={949,1,0,0,0},
[7954]={949,0,0,0,0},[7955]={949,1,0,0,0},[7956]={949,0,0,0,0},[7957]={949,1,0,0,0},
[7960]={949,0,0,0,1},[7961]={949,1,0,0,1},[7962]={949,0,0,0,1},[7963]={949,1,0,0,1},
[7964]={949,0,0,0,1},[7965]={949,1,0,0,1},[7968]={951,0,0,0,0},[7969]={951,1,0,0,0},
[7970]={951,0,0,0,0},[7971]={951,1,0,0,0},[7972]={951,0,0,0,0},[7973]={951,1,0,0,0},
[7974]={951,0,0,0,0},[7975]={951,1,0,0,0},[7976]={951,0,0,0,1},[7977]={951,1,0,0,1},
[7978]={951,0,0,0,1},[7979]={951,1,0,0,1},[7980]={951,0,0,0,1},[7981]={951,1,0,0,1},
[7982]={951,0,0,0,1},[7983]={951,1,0,0,1},[7984]={953,0,0,0,0},[7985]={953,1,0,0,0},
[7986]={953,0,0,0,0},[7987]={953,1,0,0,0},[7988]={953,0,0,0,0},[7989]={953,1,0,0,0},
[7990]={953,0,0,0,0},[7991]={953,1,0,0,0},[7992]={953,0,0,0,1},[7993]={953,1,0,0,1},
[7994]={953,0,0,0,1},[7995]={953,1,0,0,1},[7996]={953,0,0,0,1},[7997]={953,1,0,0,1},
[7998]={953,0,0,0,1},[7999]={953,1,0,0,1},[8000]={959,0,0,0,0},[8001]={959,1,0,0,0},
[8002]={959,0,0,0,0},[8003]={959,1,0,0,0},[8004]={959,0,0,0,0},[8005]={959,1,0,0,0},
[8008]={959,0,0,0,1},[8009]={959,1,0,0,1},[8010]={959,0,0,0,1},[8011]={959,1,0,0,1},
[8012]={959,0,0,0,1},[8013]={959,1,0,0,1},[8016]={965,0,0,0,0},[8017]={965,1,0,0,0},
[8018]={965,0,0,0,0},[8019]={965,1,0,0,0},[8020]={965,0,0,0,0},[8021]={965,1,0,0,0},
[8022]={965,0,0,0,0},[8023]={965,1,0,0,0},[8025]={965,1,0,0,1},[8027]={965,1,0,0,1},
[8029]={965,1,0,0,1},[8031]={965,1,0,0,1},[8032]={969,0,0,0,0},[8033]={969,1,0,0,0},
[8034]={969,0,0,0,0},[8035]={969,1,0,0,0},[8036]={969,0,0,0,0},[8037]={969,1,0,0,0},
[8038]={969,0,0,0,0},[8039]={969,1,0,0,0},[8040]={969,0,0,0,1},[8041]={969,1,0,0,1},
[8042]={969,0,0,0,1},[8043]={969,1,0,0,1},[8044]={969,0,0,0,1},[8045]={969,1,0,0,1},
[8046]={969,0,0,0,1},[8047]={969,1,0,0,1},[8048]={945,0,0,0,0},[8049]={945,0,0,0,0},
[8050]={949,0,0,0,0},[8051]={949,0,0,0,0},[8052]={951,0,0,0,0},[8053]={951,0,0,0,0},
[8054]={953,0,0,0,0},[8055]={953,0,0,0,0},[8056]={959,0,0,0,0},[8057]={959,0,0,0,0},
[8058]={965,0,0,0,0},[8059]={965,0,0,0,0},[8060]={969,0,0,0,0},[8061]={969,0,0,0,0},
[8064]={945,0,1,0,0},[8065]={945,1,1,0,0},[8066]={945,0,1,0,0},[8067]={945,1,1,0,0},
[8068]={945,0,1,0,0},[8069]={945,1,1,0,0},[8070]={945,0,1,0,0},[8071]={945,1,1,0,0},
[8072]={945,0,1,0,1},[8073]={945,1,1,0,1},[8074]={945,0,1,0,1},[8075]={945,1,1,0,1},
[8076]={945,0,1,0,1},[8077]={945,1,1,0,1},[8078]={945,0,1,0,1},[8079]={945,1,1,0,1},
[8080]={951,0,1,0,0},[8081]={951,1,1,0,0},[8082]={951,0,1,0,0},[8083]={951,1,1,0,0},
[8084]={951,0,1,0,0},[8085]={951,1,1,0,0},[8086]={951,0,1,0,0},[8087]={951,1,1,0,0},
[8088]={951,0,1,0,1},[8089]={951,1,1,0,1},[8090]={951,0,1,0,1},[8091]={951,1,1,0,1},
[8092]={951,0,1,0,1},[8093]={951,1,1,0,1},[8094]={951,0,1,0,1},[8095]={951,1,1,0,1},
[8096]={969,0,1,0,0},[8097]={969,1,1,0,0},[8098]={969,0,1,0,0},[8099]={969,1,1,0,0},
[8100]={969,0,1,0,0},[8101]={969,1,1,0,0},[8102]={969,0,1,0,0},[8103]={969,1,1,0,0},
[8104]={969,0,1,0,1},[8105]={969,1,1,0,1},[8106]={969,0,1,0,1},[8107]={969,1,1,0,1},
[8108]={969,0,1,0,1},[8109]={969,1,1,0,1},[8110]={969,0,1,0,1},[8111]={969,1,1,0,1},
[8112]={945,0,0,0,0},[8113]={945,0,0,0,0},[8114]={945,0,1,0,0},[8115]={945,0,1,0,0},
[8116]={945,0,1,0,0},[8118]={945,0,0,0,0},[8119]={945,0,1,0,0},[8120]={945,0,0,0,1},
[8121]={945,0,0,0,1},[8122]={945,0,0,0,1},[8123]={945,0,0,0,1},[8124]={945,0,1,0,1},
[8126]={953,0,1,0,0},[8130]={951,0,1,0,0},[8131]={951,0,1,0,0},[8132]={951,0,1,0,0},
[8134]={951,0,0,0,0},[8135]={951,0,1,0,0},[8136]={949,0,0,0,1},[8137]={949,0,0,0,1},
[8138]={951,0,0,0,1},[8139]={951,0,0,0,1},[8140]={951,0,1,0,1},[8144]={953,0,0,0,0},
[8145]={953,0,0,0,0},[8146]={953,0,0,1,0},[8147]={953,0,0,1,0},[8150]={953,0,0,0,0},
[8151]={953,0,0,1,0},[8152]={953,0,0,0,1},[8153]={953,0,0,0,1},[8154]={953,0,0,0,1},
[8155]={953,0,0,0,1},[8160]={965,0,0,0,0},[8161]={965,0,0,0,0},[8162]={965,0,0,1,0},
[8163]={965,0,0,1,0},[8164]={961,0,0,0,0},[8165]={961,1,0,0,0},[8166]={965,0,0,0,0},
[8167]={965,0,0,1,0},[8168]={965,0,0,0,1},[8169]={965,0,0,0,1},[8170]={965,0,0,0,1},
[8171]={965,0,0,0,1},[8172]={961,1,0,0,1},[8178]={969,0,1,0,0},[8179]={969,0,1,0,0},
[8180]={969,0,1,0,0},[8182]={969,0,0,0,0},[8183]={969,0,1,0,0},[8184]={959,0,0,0,1},
[8185]={959,0,0,0,1},[8186]={969,0,0,0,1},[8187]={969,0,0,0,1},[8188]={969,0,1,0,1},
}
local LAT = { [0x3B1]="a", [0x3B2]="b", [0x3B3]="g", [0x3B4]="d", [0x3B5]="e",
  [0x3B6]="z", [0x3B7]="ē", [0x3B8]="th", [0x3B9]="i", [0x3BA]="k", [0x3BB]="l",
  [0x3BC]="m", [0x3BD]="n", [0x3BE]="x", [0x3BF]="o", [0x3C0]="p", [0x3C1]="r",
  [0x3C2]="s", [0x3C3]="s", [0x3C4]="t", [0x3C5]="y", [0x3C6]="ph", [0x3C7]="ch",
  [0x3C8]="ps", [0x3C9]="ō" }
local ISUB = { [0x3B1] = "ą", [0x3B7] = "ę̄", [0x3C9] = "ǭ" }       -- iota subscrito
local ANTES_U = { [0x3B1] = true, [0x3B5] = true, [0x3B7] = true, [0x3BF] = true }
local NASAL = { [0x3B3] = true, [0x3BA] = true, [0x3BE] = true, [0x3C7] = true }
local MAIUSC = { ["ē"] = "Ē", ["ō"] = "Ō", ["ą"] = "Ą" }

function EB.translit_grc(palavra)
  local L = {}
  for _, cp in utf8.codes(palavra) do
    local d = D[cp]
    if d then
      L[#L + 1] = { b = d[1], r = d[2] == 1, i = d[3] == 1, d = d[4] == 1, u = d[5] == 1 }
    elseif cp >= 0x391 and cp <= 0x3A9 then
      L[#L + 1] = { b = cp + 32, u = true }
    elseif LAT[cp] then
      L[#L + 1] = { b = cp }
    elseif #L > 0 then              -- sinais combinantes (texto já decomposto)
      if cp == 0x314 then L[#L].r = true
      elseif cp == 0x345 then L[#L].i = true
      elseif cp == 0x308 then L[#L].d = true end
    end
  end
  if #L == 0 then return "" end
  local out, aspirada = {}, false
  for k, x in ipairs(L) do
    local b, prox, ant = x.b, L[k + 1], L[k - 1]
    if x.r and b ~= 0x3C1 then aspirada = true end
    local s
    if b == 0x3B3 and prox and NASAL[prox.b] then s = "n"
    elseif b == 0x3C5 then
      if (ant and ANTES_U[ant.b] and not x.d) or (prox and prox.b == 0x3B9 and not prox.d) then
        s = "u" else s = "y" end
    elseif b == 0x3C1 and x.r then s = "rh"
    elseif x.i and ISUB[b] then s = ISUB[b]
    else s = LAT[b] or "" end
    out[#out + 1] = s
  end
  local res = table.concat(out)
  if aspirada then res = "h" .. res end
  if L[1].u then
    local primeiro = utf8.char(utf8.codepoint(res, 1))
    res = (MAIUSC[primeiro] or primeiro:upper()) .. res:sub(#primeiro + 1)
  end
  return res
end

-- ----------------------- chave de ordenação para o índice (sem diacríticos)
local DOBRA = { ["ā"]="a", ["ē"]="e", ["ī"]="i", ["ō"]="o", ["ū"]="u", ["ǭ"]="o",
  ["ą"]="a", ["ę"]="e", ["ę̄"]="e", ["ǫ"]="o", ["Ā"]="A", ["Ē"]="E", ["Ō"]="O" }
function EB.chave(lema, lingua)
  local k = (lingua == nil or lingua == "grego") and EB.translit_grc(lema) or lema
  for de, para in pairs(DOBRA) do k = k:gsub(de, para) end
  k = k:gsub("\u{0304}", ""):gsub("\u{0328}", "")
  return k:lower()
end

-- ------------------------------------ hebraico: remover acentos (te'amim)
function EB.sem_acentos(s)
  local t = {}
  for _, cp in utf8.codes(s) do
    if not ((cp >= 0x0591 and cp <= 0x05AF) or cp == 0x05BD or cp == 0x05C0) then
      t[#t + 1] = utf8.char(cp)
    end
  end
  return table.concat(t)
end

local function preparar(reg, lingua, acentos)
  local w = reg.palavra or ""
  if (lingua == "hebraico" or lingua == "aramaico") and not acentos then
    w = EB.sem_acentos(w)
  end
  local tr = reg.translit or ""
  if tr == "" and lingua == "grego" then tr = EB.translit_grc(w) end
  return w, tr
end

-- ------------------------------------------------------ interlinear em linha
function EB.interlinear(caminho, lingua, de, ate, acentos, indexar)
  local ultimo, lemas_vistos = nil, {}
  for _, reg in ipairs(EB.ler(caminho)) do
    if no_intervalo(reg, de, ate) then
      local chave = reg.cap * 1000 + reg.vers
      if chave ~= ultimo then
        tex.sprint("\\EBivers{" .. reg.cap .. "}{" .. reg.vers .. "}")
        ultimo = chave
      end
      local w, tr = preparar(reg, lingua, acentos)
      tex.sprint(string.format("\\EBiw{%s}{%s}{%s}{%s}{%s}{%s}{%s}{%s}",
        esc(w), esc(tr), esc(reg.lema), esc(reg.strong), esc(reg.morf),
        esc(reg.pt), esc(reg.en), esc(reg.var)))
      if indexar and reg.lema ~= "" and not lemas_vistos[reg.lema] then
        lemas_vistos[reg.lema] = true
        local chave_idx = EB.chave(reg.lema, lingua)
        tex.sprint("\\EBindexlema{" .. lingua .. "}{" .. esc(chave_idx) .. "}{" .. esc(reg.lema) .. "}")
      end
    end
  end
end

-- ------------------------------------------------ texto corrido do trecho
function EB.texto(caminho, lingua, de, ate, acentos, numeros)
  local ultimo, partes = nil, {}
  for _, reg in ipairs(EB.ler(caminho)) do
    if no_intervalo(reg, de, ate) then
      local chave = reg.cap * 1000 + reg.vers
      local pedaco = ""
      if numeros and chave ~= ultimo then
        pedaco = "\\EBvsup{" .. reg.vers .. "}"
        ultimo = chave
      end
      local w = preparar(reg, lingua, acentos)
      pedaco = pedaco .. esc(w)
      if (reg.var or "") ~= "" then pedaco = pedaco .. "\\EBvarmark{}" end
      partes[#partes + 1] = pedaco
    end
  end
  local saida = {}
  for i, p in ipairs(partes) do
    saida[#saida + 1] = p
    if i < #partes and not p:match("\u{05BE}$") then saida[#saida + 1] = " " end
  end
  tex.sprint(table.concat(saida))
end

-- ---------------------------------------- tabela de análise morfológica
function EB.tabela(caminho, lingua, de, ate, acentos)
  for _, reg in ipairs(EB.ler(caminho)) do
    if no_intervalo(reg, de, ate) then
      local w, tr = preparar(reg, lingua, acentos)
      tex.sprint(string.format(
        "\\EBtabref{%d:%d} & \\EBtaborig{%s} & \\EBtabtr{%s} & \\EBtaborig{%s} & \\EBtabmorf{%s} & %s\\\\",
        reg.cap, reg.vers, esc(w), esc(tr), esc(reg.lema), esc(reg.morf), esc(reg.pt)))
    end
  end
end

-- ------------------------------------ vocabulário / repetições do trecho
function EB.vocabulario(caminho, lingua, de, ate, minimo)
  local cont, info, ordem, glosas = {}, {}, {}, {}
  for _, reg in ipairs(EB.ler(caminho)) do
    if no_intervalo(reg, de, ate) and (reg.lema or "") ~= "" then
      local l = reg.lema
      if not cont[l] then
        cont[l] = 0
        info[l] = reg
        ordem[#ordem + 1] = l
        glosas[l] = { lista = {}, visto = {} }
      end
      cont[l] = cont[l] + 1
      local g = reg.pt or ""
      if g ~= "" and not glosas[l].visto[g] then
        glosas[l].visto[g] = true
        table.insert(glosas[l].lista, g)
      end
    end
  end
  table.sort(ordem, function(a, b)
    if cont[a] ~= cont[b] then return cont[a] > cont[b] end
    return a < b
  end)
  for _, l in ipairs(ordem) do
    if cont[l] >= (minimo or 1) then
      local r = info[l]
      local tr = (lingua == "grego") and EB.translit_grc(l) or (r.translit or "")
      local lista = glosas[l].lista
      local g = table.concat(lista, " · ", 1, math.min(#lista, 4))
      if #lista > 4 then g = g .. " …" end
      tex.sprint(string.format("\\EBtaborig{%s} & \\EBtabtr{%s} & %s & %d & %s & %s\\\\",
        esc(l), esc(tr), esc(r.strong), cont[l], esc(r.freq_nt or ""), esc(g)))
    end
  end
end

-- ------------------------------------------- língua pela extensão do arquivo
local EXT = { grc = "grego", gr = "grego", hbo = "hebraico", heb = "hebraico",
  arc = "aramaico", syr = "siriaco", syc = "siriaco" }
function EB.lingua_de(caminho)
  local ext = (caminho or ""):match("%.(%a+)%.tsv$") or ""
  return EXT[ext:lower()] or "grego"
end

local PONT = { ",", "%.", ";", ":", "\u{00B7}", "\u{0387}", "\u{05C3}", "\u{0700}", "\u{0701}" }
local function sem_pontuacao(w)
  local mudou = true
  while mudou do
    mudou = false
    for _, p in ipairs(PONT) do
      local n
      w, n = w:gsub(p .. "$", "")
      if n > 0 then mudou = true end
    end
  end
  return w
end

-- ------------------------------ variantes (palavras vizinhas agrupadas)
function EB.variantes(caminho, lingua, de, ate)
  local grupos, atual = {}, nil
  for _, reg in ipairs(EB.ler(caminho)) do
    if no_intervalo(reg, de, ate) and (reg.var or "") ~= "" then
      local ref = reg.cap .. ":" .. reg.vers
      local w = sem_pontuacao((preparar(reg, lingua, false)))
      if atual and atual.ref == ref and atual.var == reg.var and atual.fim == reg._i - 1 then
        atual.pal = atual.pal .. " " .. w
        atual.fim = reg._i
      else
        atual = { ref = ref, var = reg.var, pal = w, fim = reg._i }
        grupos[#grupos + 1] = atual
      end
    end
  end
  for i, g in ipairs(grupos) do
    if i > 1 then tex.sprint("\\EBilvarsep") end
    tex.sprint(string.format("\\EBilvar{%s}{%s}{%s}", g.ref, esc(g.pal), esc(g.var)))
  end
  return #grupos
end

return EB
