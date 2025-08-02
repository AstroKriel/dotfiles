require("nvim-treesitter.configs").setup({
  ensure_installed = {
    "c", "cpp", "python", "lua", "vim", "vimdoc", "bash", "markdown", "markdown_inline"
  },
  auto_install = true,
  highlight = {
    enable = true,
    additional_vim_regex_highlighting = {},
  },
  indent = {
    enable = true,
    disable = { "python" },
  },
})

-- .