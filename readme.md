# 🛣️ GOINFRA — Sistema de Monitoramento Visual

Sistema web para acompanhamento de instalação de equipamentos NIS, com mapa de rotas otimizadas e painel de progresso.

---

## 📁 Estrutura do Projeto

```
VISUAL_SISTEMA/
├── login.html              ← Página de acesso (com senha)
├── index.html              ← Painel principal (cronograma)
├── rotas.html              ← Mapa de rotas
├── css/
│   └── style.css
├── js/
│   ├── auth.js             ← Proteção de páginas
│   ├── carregar_excel.js   ← Leitura do Excel
│   ├── filtros.js          ← Filtros e tabela
│   └── mapa.js             ← Mapa e rotas
└── data/
    └── cronograma_goinfra_visual.xlsx   ← ⚠️ SEU ARQUIVO AQUI
```

---

## ⚙️ Configuração

### 1. Colocar o arquivo Excel
Copie seu arquivo para:
```
data/cronograma_goinfra_visual.xlsx
```

### 2. Alterar a senha
Abra `login.html` e edite esta linha:
```javascript
const SENHA_CORRETA = "goinfra2025";  // ← mude aqui
```

### 3. Colunas esperadas no Excel
| Coluna | Descrição |
|--------|-----------|
| `nis` | Número da NIS |
| `ID_Equip` | ID do equipamento |
| `municipio` | Município |
| `rodovia` | Rodovia |
| `LATITUDE` | Coordenada (aceita vírgula ou ponto) |
| `LONGITUDE` | Coordenada |
| `ENERGIZACAO` | SOLAR ou CONVENCIONAL |
| `ONLINE` | ONLINE ou vazio |
| `Equipe_civil` | Nome da equipe civil |
| `Equipe_eletronica` | Nome da equipe elétrica |
| `FURACAO_REALIZADO` | Etapa concluída (qualquer valor = sim) |
| `FIXACAO_POSTES_REALIZADO` | Etapa concluída |
| `ESTRUTURAS_REALIZADO` | Etapa concluída |
| `TRAVESSIA_INTERLIGACAO_REALIZADO` | Etapa concluída |
| `MONTAGEM_REALIZADO` | Etapa concluída |
| `MONTAGEM_ESTRUTURAL_REALIZADO` | Etapa concluída |
| `AFERICAO_REALIZADO` | Etapa concluída |

---

## 🚀 Publicar no GitHub Pages

### Passo a passo completo:

**1. Crie o repositório no GitHub**
- Acesse [github.com](https://github.com) → "New repository"
- Nome: `goinfra-visual` (ou qualquer nome)
- Visibilidade: **Public** (obrigatório para GitHub Pages grátis)
- Clique em "Create repository"

**2. No VS Code, abra o terminal e execute:**
```bash
cd caminho/para/VISUAL_SISTEMA

git init
git add .
git commit -m "Sistema GOINFRA v2.0"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/goinfra-visual.git
git push -u origin main
```

**3. Ativar GitHub Pages**
- No repositório → **Settings** → **Pages**
- Source: `Deploy from a branch`
- Branch: `main` → pasta `/` (root)
- Clique em **Save**

**4. Acessar o sistema**
Após ~2 minutos:
```
https://SEU_USUARIO.github.io/goinfra-visual/login.html
```

---

## 🔒 Sobre a Senha

A senha é verificada no navegador via `sessionStorage`. É adequada para uso interno/equipe. Para segurança maior em produção, considere um backend com autenticação real.

**Senha padrão:** `goinfra2025`

---

## 🗺️ Funcionalidades do Mapa

- ⭐ **Próxima NIS**: Destaca em amarelo a NIS prioritária pendente
- 🔵 **Rota otimizada**: Linha azul tracejada conectando todas as pendentes (algoritmo nearest-neighbor)
- 📏 **Distâncias**: Exibe distância total da rota e km até o próximo ponto
- 🔴 **Pendentes**: Marcadores vermelhos
- 🟢 **Online**: Marcadores verdes

---

*GOINFRA © 2025*