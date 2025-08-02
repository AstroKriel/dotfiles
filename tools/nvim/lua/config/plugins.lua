-- list of plugins for lazy.nvim
return {
  -- ----------------------------------------
  -- UI & appearance
  -- ----------------------------------------

  { -- Colorscheme: Catppuccin theme with transparent background
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000, -- loaded early so it applies before other UI
    config = function()
      require("plugins.catppuccin")
    end,
  },

  { -- Show available keybindings with popup help
    "folke/which-key.nvim",
    event = "VimEnter",
    config = function()
      require("plugins.which-key")
    end,
  },

  -- ----------------------------------------
  -- File navigation & project tools
  -- ----------------------------------------

  { -- File explorer tree (we've set it to open on the RIGHT side)
    "nvim-tree/nvim-tree.lua",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("plugins.nvim-tree") -- note: tree opens on the right
    end,
  },

  { -- Fuzzy finder: search files, buffers, text, LSP symbols, etc.
    "nvim-telescope/telescope.nvim",
    event = "VimEnter",
    dependencies = {
      "nvim-lua/plenary.nvim", -- async utility lib required by Telescope

      { -- Native fzf sorter (faster than Lua fallback)
        "nvim-telescope/telescope-fzf-native.nvim",
        build = "make",
        cond = function() return vim.fn.executable("make") == 1 end,
      },

      { -- Use Telescope for UI popups (e.g. LSP code actions)
        "nvim-telescope/telescope-ui-select.nvim",
      },
    },
    config = function()
      require("plugins.telescope")
    end,
  },

  -- ----------------------------------------
  -- Code intelligence: LSP, completion, syntax
  -- ----------------------------------------

  { -- Language Server Protocol (LSP) support for C++ and Python
    "neovim/nvim-lspconfig",
    dependencies = {
      { "williamboman/mason.nvim", opts = {} },               -- install LSPs
      { "williamboman/mason-lspconfig.nvim" },                -- bridge to lspconfig
      { "WhoIsSethDaniel/mason-tool-installer.nvim" },        -- auto-install configured LSPs
    },
    config = function()
      require("plugins.lsp") -- note: uses cmp_nvim_lsp for capabilities
    end,
  },

  { -- Autocompletion engine (used with LSP and snippets)
    "hrsh7th/nvim-cmp",
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",   -- completion from LSP
      "hrsh7th/cmp-buffer",     -- completion from open buffers
      "hrsh7th/cmp-path",       -- completion from filesystem paths
      "L3MON4D3/LuaSnip",       -- snippet engine
    },
    config = function()
      require("plugins.cmp")
    end,
  },

  { -- Treesitter: better syntax highlighting and indentation
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate", -- ensures parsers are up to date
    config = function()
      require("plugins.treesitter")
    end,
  },

  -- ----------------------------------------
  -- EDITING ENHANCEMENTS
  -- ----------------------------------------

  { -- comment toggling
    "numToStr/Comment.nvim",
    event = "VeryLazy",
    config = function()
      require("plugins.comment")
    end,
  },

  { -- better "around/inside" text objects
    "echasnovski/mini.ai",
    version = "*",
    config = function()
      require("mini.ai").setup()
    end,
  },

  { -- surround editing
    "echasnovski/mini.surround",
    version = "*",
    config = function()
      require("mini.surround").setup()
    end,
  },
}

-- .