-- General scrolling with mouse
vim.keymap.set("n", "<ScrollWheelDown>", "<Cmd>keepjumps normal! gj0<CR>", { silent = true })
vim.keymap.set("n", "<ScrollWheelUp>",   "<Cmd>keepjumps normal! gk0<CR>", { silent = true })

-- File tree toggle
vim.keymap.set("n", "<leader>e", "<cmd>NvimTreeToggle<CR>", { desc = "Toggle file explorer" })

-- Telescope bindings
vim.keymap.set("n", "<leader>ff", "<cmd>Telescope find_files<cr>", { desc = "Find files" })
vim.keymap.set("n", "<leader>fg", "<cmd>Telescope live_grep<cr>",  { desc = "Live grep" })
vim.keymap.set("n", "<leader>fb", "<cmd>Telescope buffers<cr>",    { desc = "Find buffers" })

-- LSP hover popup
vim.keymap.set("n", "K", vim.lsp.buf.hover, { desc = "LSP Hover" })
vim.keymap.set("n", "<leader>k", function()
  vim.cmd("pclose")
end, { desc = "Close hover popup" })

-- .