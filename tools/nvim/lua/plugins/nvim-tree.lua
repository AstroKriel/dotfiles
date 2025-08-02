require("nvim-tree").setup({
  view = {
    width = 40,
    side = "right", -- ← move the tree to the right
    preserve_window_proportions = true,
  },
  actions = {
    open_file = {
      quit_on_open = false,
    },
  },
})

-- .