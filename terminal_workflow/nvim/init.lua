-- --------------
-- | leader key |
-- --------------

vim.g.mapleader = " "

-- -----------
-- | options |
-- -----------

-- ui
vim.opt.termguicolors = true
vim.opt.wrap = false
vim.opt.mouse = "a"

-- line numbers
vim.opt.number = true
vim.opt.relativenumber = true

-- clipboard
vim.opt.clipboard = "unnamedplus"

-- syntax
vim.cmd("syntax on")

-- ----------------
-- | key mappings |
-- ----------------

vim.keymap.set("n", "<ScrollWheelDown>", "<Cmd>keepjumps normal! gj0<CR>", { silent = true })
vim.keymap.set("n", "<ScrollWheelUp>",   "<Cmd>keepjumps normal! gk0<CR>", { silent = true })
vim.keymap.set("n", "<leader>e", "<cmd>NvimTreeToggle<CR>", { desc = "Toggle file explorer" })
vim.keymap.set("n", "<leader>ff", "<cmd>Telescope find_files<cr>", { desc = "Find files" })
vim.keymap.set("n", "<leader>fg", "<cmd>Telescope live_grep<cr>",  { desc = "Live grep" })
vim.keymap.set("n", "<leader>fb", "<cmd>Telescope buffers<cr>",    { desc = "Find buffers" })

-- ------------------------------
-- | PLUGIN MANAGER (LAZY.NVIM) |
-- ------------------------------

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  -- theme
  {
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000,
    config = function()
      require("catppuccin").setup({
        flavour = "mocha",
        transparent_background = true,
      })
      vim.cmd.colorscheme("catppuccin")
    end,
  },
  -- file explorer
  {
    "nvim-tree/nvim-tree.lua",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("nvim-tree").setup({
        view = {
          width = 40,
          side = "left",
          preserve_window_proportions = true,
        },
        actions = {
          open_file = {
            quit_on_open = false,
          },
        },
      })
    end,
  },
  -- telescope (fuzzy finder)
  {
    "nvim-telescope/telescope.nvim",
    dependencies = {
      "nvim-lua/plenary.nvim",
    },
    config = function()
      require("telescope").setup({})
    end,
  },
  -- accelerated fuzzy matcher
  {
    "nvim-telescope/telescope-fzf-native.nvim",
    build = "make",
    cond = function()
      return vim.fn.executable("make") == 1
    end,
    config = function()
      require("telescope").load_extension("fzf")
    end,
  },
})


-- .