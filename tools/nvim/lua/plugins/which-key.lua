local wk = require("which-key")

wk.setup({
  -- Open instantly when you press a mapped prefix (like <leader>)
  delay = 0,

  -- document top-level key groups
  spec = {
    { "<leader>s", group = "[S]earch" },
    { "<leader>t", group = "[T]oggle" },
    { "<leader>h", group = "Git [H]unk", mode = { "n", "v" } },
  },
})

-- .