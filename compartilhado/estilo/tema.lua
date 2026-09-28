--[[ ===========================================================================
  tema.lua — motor do "estudo temático" (LuaLaTeX)
  Lê, na pasta do tema (\temaDados):
    textos.tsv       ref, grupo, peso, nota
    vocabulario.tsv  lingua, lema, translit, strong, ocorrencias, sentido, nota
    ocorrencias.tsv  strong, lema, ref, ordem, cap, vers, forma   (opcional)
  e dados/biblia/livros.tsv para reconhecer livros e ordenar em ordem bíblica.
=========================================================================== ]]
TM = TM or {}

local function abrir(caminho)
  local f = io.open(caminho, "r")
  if not f and kpse then
    local achado = kpse.find_file(caminho, "tex")
    if achado then f = io.open(achado, "r") end
  end
  return f
end

local cache = {}
local function ler(caminho, opcional)
  if cache[caminho] then return cache[caminho] end
  local f = abrir(caminho)
  if not f then
    if not opcional then tex.error("Estudo temático: arquivo '" .. caminho .. "' não encontrado.") end
    cache[caminho] = {}
    return cache[caminho]
  end
  local cab, linhas = nil, {}
  for linha in f:lines() do
    linha = linha:gsub("\r$", "")
    if not (linha:match("^%s*#") or linha:match("^%s*$")) then
      local campos = {}
      for c in (linha .. "\t"):gmatch("(.-)\t") do campos[#campos + 1] = c end
      if not cab then cab = campos
      else
        local r = {}
        for i, nome in ipairs(cab) do r[nome] = campos[i] or "" end
        linhas[#linhas + 1] = r
      end
    end
  end
  f:close()
  cache[caminho] = linhas
  return linhas
end

local ESC = { ["\\"] = "\\textbackslash{}", ["{"] = "\\{", ["}"] = "\\}", ["%"] = "\\%",
  ["&"] = "\\&", ["#"] = "\\#", ["_"] = "\\_", ["$"] = "\\$", ["^"] = "\\^{}", ["~"] = "\\~{}" }
local function esc(s) return ((s or ""):gsub("[\\{}%%&#_%$%^~]", ESC)) end

-- ------------------------------------------------ livros e referências
local ACENTOS = { ["á"]="a", ["à"]="a", ["â"]="a", ["ã"]="a", ["é"]="e", ["ê"]="e", ["í"]="i",
  ["ó"]="o", ["ô"]="o", ["õ"]="o", ["ú"]="u", ["ç"]="c", ["Á"]="a", ["Ê"]="e", ["É"]="e",
  ["Ó"]="o", ["Í"]="i", ["Ú"]="u" }
local function chave_nome(s)
  s = s:gsub("[%z\1-\127\194-\244][\128-\191]*", function(c) return ACENTOS[c] or c end)
  return s:lower():gsub("%s+", "")
end

local LIVROS, POR_NOME = nil, {}
local function livros()
  if LIVROS then return LIVROS end
  LIVROS = ler("dados/biblia/livros.tsv")
  for _, b in ipairs(LIVROS) do
    POR_NOME[chave_nome(b.abrev)] = b
    POR_NOME[chave_nome(b.nome)] = b
    for alt in (b.nomes_alt or ""):gmatch("[^|]+") do POR_NOME[chave_nome(alt)] = b end
  end
  return LIVROS
end

-- "Lv 17:10-14" -> livro, cap, vers
function TM.analisar(ref)
  livros()
  local nome, cap, vers = (ref or ""):match("^%s*(.-)%s*(%d+):(.-)%s*$")
  if not nome then return nil end
  return POR_NOME[chave_nome(nome)], tonumber(cap), vers
end

local function ordenar(a, b)
  if a._ordem ~= b._ordem then return a._ordem < b._ordem end
  if a._cap ~= b._cap then return a._cap < b._cap end
  return a._v1 < b._v1
end

local function preparar(lista)
  for _, t in ipairs(lista) do
    if not t._ordem then
      local b, cap, vers = TM.analisar(t.ref)
      t._livro = b
      t._ordem = b and tonumber(b.ordem) or 99
      t._cap = cap or 0
      t._vers = vers or ""
      t._v1 = tonumber((vers or ""):match("%d+")) or 0
      t._nome = b and (b.nome .. " " .. cap .. ":" .. vers) or t.ref
    end
  end
  return lista
end

local function idx(t)
  if not t._livro then return "" end
  return string.format("%02d@%s!%03d%03d@%d:%s", t._ordem, esc(t._livro.nome), t._cap, t._v1,
    t._cap, esc(t._vers))
end

function TM.indice(ref)
  local t = preparar({ { ref = ref } })[1]
  if t._livro then tex.sprint("\\index[textos]{" .. idx(t) .. "}") end
end

function TM.nome(ref)
  local t = preparar({ { ref = ref } })[1]
  tex.sprint(esc(t._nome))
end

-- ------------------------------------------------ catálogo de textos
function TM.textos(dados) return preparar(ler(dados .. "/textos.tsv")) end

function TM.tabela(dados, modo, grupo_so, peso_so)
  peso_so = peso_so or ""
  local todos, lista = TM.textos(dados), {}
  for _, t in ipairs(todos) do
    if peso_so == "" or t.peso == peso_so then lista[#lista + 1] = t end
  end
  if #lista == 0 then tex.sprint("\\EBtemavazio\\\\"); return end
  if modo == "biblica" then
    local copia = {}
    for _, t in ipairs(lista) do if grupo_so == "" or t.grupo == grupo_so then copia[#copia + 1] = t end end
    table.sort(copia, ordenar)
    for _, t in ipairs(copia) do
      tex.sprint(string.format("\\EBtematexto{%s}{%s}{%s}{%s}{%s}\\\\",
        esc(t._nome), esc(t.grupo), esc(t.peso), esc(t.nota), idx(t)))
    end
    return
  end
  local ordem_g, por_g = {}, {}
  for _, t in ipairs(lista) do
    local g = t.grupo ~= "" and t.grupo or "Outros"
    if not por_g[g] then por_g[g] = {}; ordem_g[#ordem_g + 1] = g end
    table.insert(por_g[g], t)
  end
  for _, g in ipairs(ordem_g) do
    if grupo_so == "" or grupo_so == g then
      table.sort(por_g[g], ordenar)
      tex.sprint(string.format("\\EBtemagrupo{%s}{%d}\\\\", esc(g), #por_g[g]))
      for _, t in ipairs(por_g[g]) do
        tex.sprint(string.format("\\EBtematexto{%s}{%s}{%s}{%s}{%s}\\\\",
          esc(t._nome), esc(g), esc(t.peso), esc(t.nota), idx(t)))
      end
    end
  end
end

-- ------------------------------------------------ vocabulário
function TM.vocabulario(dados)
  for _, v in ipairs(ler(dados .. "/vocabulario.tsv", true)) do
    local tr = v.translit
    if (tr == nil or tr == "") and v.lingua == "grego" and EB and EB.translit_grc then
      tr = EB.translit_grc(v.lema)
    end
    tex.sprint(string.format("\\EBtemavoc{%s}{%s}{%s}{%s}{%s}{%s}{%s}\\\\",
      esc(v.lingua), esc(v.lema), esc(tr), esc(v.strong), esc(v.ocorrencias), esc(v.sentido), esc(v.nota)))
  end
end

-- ------------------------------------------------ distribuição por grupo de livros
function TM.distribuicao(dados)
  livros()
  local grupos, nomes = {}, {}
  for _, b in ipairs(LIVROS) do
    local g = b.testamento .. " · " .. b.grupo
    if not grupos[g] then grupos[g] = { t = 0, o = 0 }; nomes[#nomes + 1] = g end
    b._g = g
  end
  for _, t in ipairs(TM.textos(dados)) do
    if t._livro then grupos[t._livro._g].t = grupos[t._livro._g].t + 1 end
  end
  local oc = ler(dados .. "/ocorrencias.tsv", true)
  for _, o in ipairs(oc) do
    local b = LIVROS[tonumber(o.ordem) or 0]
    if b then grupos[b._g].o = grupos[b._g].o + 1 end
  end
  local mt, mo = 1, 1
  for _, g in ipairs(nomes) do mt = math.max(mt, grupos[g].t); mo = math.max(mo, grupos[g].o) end
  for _, g in ipairs(nomes) do
    tex.sprint(string.format("\\EBtemabarra{%s}{%d}{%d}{%d}{%d}\\\\", esc(g), grupos[g].t, mt,
      grupos[g].o, mo))
  end
end

-- ------------------------------------------------ todas as ocorrências (apêndice)
function TM.ocorrencias(dados, strong)
  livros()
  local cobertos = {}
  for _, t in ipairs(TM.textos(dados)) do
    if t._livro then
      for p in (t._vers .. ","):gmatch("([^,;]+)[,;]") do
        local a, b = p:match("(%d+)%s*[-–]%s*(%d+)")
        a = tonumber(a or p:match("%d+")); b = tonumber(b) or a
        if a then for v = a, b do cobertos[t._livro.abrev .. " " .. t._cap .. ":" .. v] = true end end
      end
    end
  end
  local atual, cap_atual, partes, blocos, lema = nil, nil, {}, {}, ""
  local function fechar()
    if atual then
      tex.sprint(string.format("\\EBtemaoclivro{%s}{%s}", esc(atual), table.concat(blocos, "; ")))
    end
  end
  local vistos = {}
  for _, o in ipairs(ler(dados .. "/ocorrencias.tsv", true)) do
    if strong == "" or o.strong == strong then
      lema = o.lema
      local b = LIVROS[tonumber(o.ordem) or 0]
      local chave = o.ref
      if b and not vistos[chave] then
        vistos[chave] = true
        if b.nome ~= atual then
          if #partes > 0 then blocos[#blocos + 1] = cap_atual .. ":" .. table.concat(partes, ", ") end
          fechar(); atual, cap_atual, partes, blocos = b.nome, nil, {}, {}
        end
        if o.cap ~= cap_atual then
          if #partes > 0 then blocos[#blocos + 1] = cap_atual .. ":" .. table.concat(partes, ", ") end
          cap_atual, partes = o.cap, {}
        end
        local v = o.vers
        if cobertos[b.abrev .. " " .. o.cap .. ":" .. o.vers] then v = "\\EBtemacoberto{" .. v .. "}" end
        partes[#partes + 1] = v
      end
    end
  end
  if #partes > 0 then blocos[#blocos + 1] = cap_atual .. ":" .. table.concat(partes, ", ") end
  fechar()
end

-- ------------------------------------------------ números para o texto
function TM.numeros(dados)
  local lista, grupos, ng = TM.textos(dados), {}, 0
  for _, t in ipairs(lista) do
    if not grupos[t.grupo] then grupos[t.grupo] = true; ng = ng + 1 end
  end
  local oc = ler(dados .. "/ocorrencias.tsv", true)
  tex.sprint(string.format("\\def\\temaNTextos{%d}\\def\\temaNGrupos{%d}\\def\\temaNOcorrencias{%d}",
    #lista, ng, #oc))
end

return TM
