vim.opt.clipboard = "unnamedplus"
vim.opt.number = true
vim.opt.relativenumber = true
vim.cmd("syntax on")
vim.opt.mouse = "a"
vim.keymap.set("n", "<ScrollWheelDown>", "<Cmd>keepjumps normal! gj<CR>", { silent = true })
vim.keymap.set("n", "<ScrollWheelUp>",   "<Cmd>keepjumps normal! gk<CR>", { silent = true })
