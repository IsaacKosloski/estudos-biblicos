--[[ ===========================================================================
  livro.lua — motor do "estudo de livro" (LuaLaTeX)
  Lê  <dados>/licoes.tsv  (num, parte, titulo, pagina, pagina_pdf)
      <dados>/textos.tsv  (licao, secao, ref, abrev, ordem, cap, vers, tipo)
      dados/biblia/livros.tsv (ordem, abrev, nome, capitulos, testamento, grupo)
  e escreve as macros que montam o caderno (ver livro.sty).
=========================================================================== ]]
LV = LV or {}

local function abrir(caminho)
  local f = io.open(caminho, "r")
  if not f and kpse then
    local achado = kpse.find_file(caminho, "tex")
    if achado then f = io.open(achado, "r") end
  end
  return f
end

local cache = {}
local function ler(caminho)
  if cache[caminho] then return cache[caminho] end
  local f = abrir(caminho)
  if not f then
    tex.error("Estudo de livro: arquivo '" .. caminho .. "' não encontrado.")
    return {}
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

-- "1-12,20" -> conjunto de números
local function faixa(spec)
  if not spec or spec:match("^%s*$") then return nil end
  local sel = {}
  for pedaco in spec:gmatch("[^,]+") do
    local a, b = pedaco:match("^%s*(%d+)%s*%-%s*(%d+)%s*$")
    if a then for i = tonumber(a), tonumber(b) do sel[i] = true end
    else local n = tonumber(pedaco:match("%d+")); if n then sel[n] = true end end
  end
  return sel
end

function LV.licoes(dados) return ler(dados .. "/licoes.tsv") end
function LV.textos(dados) return ler(dados .. "/textos.tsv") end

-- ------------------------------------------------ gera o corpo do caderno
function LV.gerar(dados, spec)
  local sel, licoes = faixa(spec), LV.licoes(dados)
  local parte_atual = nil
  local primeira, ultima = {}, {}
  for _, l in ipairs(licoes) do
    if not primeira[l.parte] then primeira[l.parte] = l.num end
    ultima[l.parte] = l.num
  end
  for i, l in ipairs(licoes) do
    local n = tonumber(l.num)
    if not sel or sel[n] then
      if l.parte ~= "" and l.parte ~= parte_atual then
        tex.sprint("\\EBlivparte{" .. esc(l.parte) .. "}{\\livroUnidadePlural\\ "
          .. primeira[l.parte] .. "–" .. ultima[l.parte] .. "}")
        parte_atual = l.parte
      end
      local prox = licoes[i + 1]
      local fim = prox and (tonumber(prox.pagina) or 0) - 1 or (tonumber(l.pagina) or 0) + 3
      tex.sprint(string.format("\\EBlivlicao{%s}{%s}{%s}{%s}{%s}",
        l.num, esc(l.titulo), esc(l.pagina), tostring(fim), esc(l.pagina_pdf)))
    end
  end
end

-- chave de ordenação do índice de textos: livro, capítulo, 1º versículo
local function chave_idx(t)
  local v1 = tonumber((t.vers or ""):match("%d+")) or 0
  return string.format("%02d", tonumber(t.ordem) or 0),
         string.format("%03d%03d", tonumber(t.cap) or 0, v1)
end

-- ------------------------------------------ tabela de textos de uma lição
function LV.tabela(dados, num, impresso)
  local livros = {}
  for _, b in ipairs(ler("dados/biblia/livros.tsv")) do livros[b.ordem] = b end
  local n = 0
  for _, t in ipairs(LV.textos(dados)) do
    if t.licao == num then
      n = n + 1
      local k1, k2 = chave_idx(t)
      local nome = livros[t.ordem] and livros[t.ordem].nome or t.ref
      tex.sprint(string.format("\\EBlivtexto{%s}{%s}{%s}{%s@%s}{%s@%s:%s}\\\\",
        esc(t.secao), esc(t.ref), esc(t.tipo), k1, esc(nome), k2, esc(t.cap), esc(t.vers)))
    end
  end
  if n == 0 then tex.sprint("\\EBlivsemtextos\\\\") end
end

function LV.contagem(dados, num)
  local n, leia = LV.contar(dados, num)
  tex.sprint("\\EBlivnumeros{" .. n .. "}{" .. leia .. "}")
end

function LV.contar(dados, num)
  local n, leia = 0, 0
  for _, t in ipairs(LV.textos(dados)) do
    if t.licao == num then n = n + 1; if t.tipo == "leia" then leia = leia + 1 end end
  end
  return n, leia
end

-- ------------------------------------------------- textos mais citados
function LV.mais_citados(dados, minimo, maximo)
  local cont, ordem, onde, info = {}, {}, {}, {}
  for _, t in ipairs(LV.textos(dados)) do
    local k = t.abrev
    if not cont[k] then cont[k] = 0; onde[k] = {}; info[k] = t; ordem[#ordem + 1] = k end
    cont[k] = cont[k] + 1
    table.insert(onde[k], tonumber(t.licao) and string.format("%d", tonumber(t.licao)) or t.licao)
  end
  table.sort(ordem, function(a, b)
    if cont[a] ~= cont[b] then return cont[a] > cont[b] end
    local ia, ib = info[a], info[b]
    if ia.ordem ~= ib.ordem then return tonumber(ia.ordem) < tonumber(ib.ordem) end
    return (tonumber(ia.cap) or 0) < (tonumber(ib.cap) or 0)
  end)
  local n = 0
  for _, k in ipairs(ordem) do
    if cont[k] >= (minimo or 2) and n < (maximo or 40) then
      n = n + 1
      tex.sprint(string.format("%s & %d & %s\\\\", esc(info[k].ref), cont[k], table.concat(onde[k], ", ")))
    end
  end
end

-- ------------------------------------------ distribuição por livro bíblico
function LV.por_livro(dados)
  local cont, livros = {}, ler("dados/biblia/livros.tsv")
  for _, t in ipairs(LV.textos(dados)) do cont[t.ordem] = (cont[t.ordem] or 0) + 1 end
  local partes = {}
  for _, b in ipairs(livros) do
    if cont[b.ordem] then partes[#partes + 1] = b.abrev .. "\\,(" .. cont[b.ordem] .. ")" end
  end
  tex.sprint(table.concat(partes, " \\textperiodcentered{} "))
end

-- --------------------------------------------------- registro de progresso
function LV.progresso(dados)
  for _, l in ipairs(LV.licoes(dados)) do
    local n, leia = LV.contar(dados, l.num)
    tex.sprint(string.format("\\EBlivprog{%s}{%s}{%s}{%d}{%d}\\\\", l.num, esc(l.titulo), esc(l.pagina), n, leia))
  end
end

-- ----------------------------------------- leitura da Bíblia (66 livros)
function LV.leitura()
  local grupo = nil
  for _, b in ipairs(ler("dados/biblia/livros.tsv")) do
    local g = b.testamento .. ": " .. b.grupo
    if g ~= grupo then
      tex.sprint("\\EBlivgrupo{" .. (b.testamento == "AT" and "Escrituras Hebraicas" or "Escrituras Gregas")
        .. "}{" .. esc(b.grupo) .. "}")
      grupo = g
    end
    local caixas = {}
    for c = 1, tonumber(b.capitulos) do caixas[#caixas + 1] = "\\EBcx{" .. c .. "}" end
    tex.sprint("\\EBlivlivro{" .. esc(b.nome) .. "}{" .. table.concat(caixas) .. "}")
  end
end

return LV
