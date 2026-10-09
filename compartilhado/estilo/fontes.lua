--[[ ===========================================================================
  fontes.lua — cuidados com as fontes do repositório (LuaLaTeX)

  O luaotfload guarda um cache de cada fonte (pasta .../luatex-cache/generic/
  fonts/otl) com o nome da fonte como chave e o CAMINHO COMPLETO do arquivo
  dentro. Se o repositório muda de lugar (outra pasta, outro clone, outro
  computador com o mesmo usuário), o cache continua apontando para o caminho
  antigo: as páginas são compostas normalmente, mas no fim o LuaTeX não acha o
  arquivo para embutir no PDF e para com

      ! error:  (file ) (type 2): cannot find file ''

  EBF.limpar_cache(pasta) apaga, antes de carregar as fontes, só as entradas do
  cache das NOSSAS fontes cujo caminho guardado não existe mais. Elas são
  recriadas automaticamente na mesma compilação (alguns segundos a mais).
=========================================================================== ]]
EBF = EBF or {}

-- "/a/b/estilo/../fontes/" -> "/a/b/fontes/"
function EBF.normalizar(p)
  if not p then return p end
  local antes
  repeat
    antes = p
    p = p:gsub("/[^/]+/%.%./", "/", 1)
  until p == antes
  p = p:gsub("/%./", "/")
  return p
end

local function existe(p)
  if not p or p == "" then return false end
  local f = io.open(p, "rb")
  if f then f:close(); return true end
  return false
end

local function pastas_do_cache()
  local fl = luaotfload and luaotfload.fontloader
  local caches = fl and fl.caches
  local lista, vistas = {}, {}
  local function por(p)
    if type(p) == "string" and p ~= "" and not vistas[p] then
      vistas[p] = true; lista[#lista + 1] = p
    end
  end
  if caches then
    local ok, w = pcall(caches.getwritablepath, "fonts", "otl")
    if ok then por(w) end
    local ok2, r = pcall(caches.getreadablepaths, "fonts", "otl")
    if ok2 and type(r) == "table" then for _, p in ipairs(r) do por(p) end end
  end
  return lista
end

function EBF.limpar_cache(dir)
  if not (lfs and dir and lfs.isdir and lfs.isdir(dir)) then return end
  local pastas = pastas_do_cache()
  if #pastas == 0 then return end
  local removidas = 0
  for arquivo in lfs.dir(dir) do
    local base = arquivo:match("^(.-)%.[oOtT][tT][fF]$")
    if base then
      local nome = base:lower()
      for _, p in ipairs(pastas) do
        local lua = p .. "/" .. nome .. ".lua"
        local f = io.open(lua, "rb")
        if f then
          local txt = f:read("*a") or ""
          f:close()
          local guardado = txt:match('%["filename"%]="([^"]*)"')
          if guardado and not existe(guardado) then
            os.remove(lua)
            os.remove(p .. "/" .. nome .. ".luc")
            removidas = removidas + 1
          end
        end
      end
    end
  end
  if removidas > 0 then
    texio.write_nl("log", "estudobiblico: " .. removidas
      .. " entrada(s) antiga(s) do cache de fontes removida(s) (o repositorio mudou de pasta).")
  end
end

return EBF
