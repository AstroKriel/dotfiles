local telescope = require("telescope")
local builtin = require("telescope.builtin")

telescope.setup({
  extensions = {
    ["ui-select"] = require("telescope.themes").get_dropdown(),
  },
})

-- load extensions
pcall(telescope.load_extension, "fzf")
pcall(telescope.load_extension, "ui-select")

-- keybindings
vim.keymap.set("n", "<leader>sf", builtin.find_files, { desc = "[S]earch [F]iles" })
vim.keymap.set("n", "<leader>sg", builtin.live_grep,  { desc = "[S]earch by [G]rep" })
vim.keymap.set("n", "<leader>sb", builtin.buffers,    { desc = "[S]earch [B]uffers" })
vim.keymap.set("n", "<leader>sh", builtin.help_tags,  { desc = "[S]earch [H]elp" })
vim.keymap.set("n", "<leader>sk", builtin.keymaps,    { desc = "[S]earch [K]eymaps" })
vim.keymap.set("n", "<leader>sr", builtin.resume,     { desc = "[S]earch [R]esume" })

-- special case: fuzzy search in current buffer
vim.keymap.set("n", "<leader>/", function()
  builtin.current_buffer_fuzzy_find(require("telescope.themes").get_dropdown {
    winblend = 10,
    previewer = false,
  })
end, { desc = "[/] Search in current buffer" })

-- .