-- ========================================
-- LEADER KEY
-- ========================================

vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- ========================================
-- UI OPTIONS
-- ========================================

vim.opt.termguicolors = true
vim.opt.wrap = false
vim.opt.mouse = "a"
vim.o.signcolumn = "yes"
vim.o.splitright = true
vim.o.splitbelow = true

-- show invisible characters
vim.o.list = true
vim.opt.listchars = {
  tab = "» ",
  trail = "·",
  nbsp = "␣",
}

-- preview :substitute live in a split
vim.o.inccommand = "split"

-- ========================================
-- LINE NUMBERS & CURSOR
-- ========================================

vim.o.cursorline = true
vim.opt.number = true
vim.opt.relativenumber = true

-- ========================================
-- CLIPBOARD
-- ========================================

vim.schedule(function()
  vim.o.clipboard = "unnamedplus"
end)

-- ========================================
-- SYNTAX & SEARCH
-- ========================================

vim.cmd("syntax on")

vim.o.ignorecase = true
vim.o.smartcase = true
vim.o.timeoutlen = 300

-- ========================================
-- EDITING & BEHAVIOR
-- ========================================

vim.o.updatetime = 250
vim.o.undofile = true
vim.o.confirm = true

-- .