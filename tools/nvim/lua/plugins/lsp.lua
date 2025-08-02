-- make all lsp floating windows use a rounded white border
local float_opts = { border = "rounded", max_width=80, focusable = false }
vim.lsp.handlers["textDocument/hover"] = vim.lsp.with(vim.lsp.handlers.hover, float_opts)
vim.lsp.handlers["textDocument/signatureHelp"] = vim.lsp.with(vim.lsp.handlers.signature_help, float_opts)
vim.api.nvim_set_hl(0, "NormalFloat",  { bg = "black" })
vim.api.nvim_set_hl(0, "FloatBorder", { fg = "white", bg = "black" })

-- create capabilities using standard nvim-cmp support
local capabilities = require("cmp_nvim_lsp").default_capabilities()

-- setup lsp-related keymaps and inlay hints when the lsp attaches
vim.api.nvim_create_autocmd("LspAttach", {
  group = vim.api.nvim_create_augroup("user-lsp-attach", { clear = true }),
  callback = function(event)
    local map = function(keys, func, desc, mode)
      vim.keymap.set(mode or "n", keys, func, { buffer = event.buf, desc = "LSP: " .. desc })
    end

    map("grn", vim.lsp.buf.rename, "[R]e[n]ame")
    map("gra", vim.lsp.buf.code_action, "[G]oto Code [A]ction", { "n", "x" })
    map("grr", require("telescope.builtin").lsp_references, "[G]oto [R]eferences")
    map("gri", require("telescope.builtin").lsp_implementations, "[G]oto [I]mplementation")
    map("grd", require("telescope.builtin").lsp_definitions, "[G]oto [D]efinition")
    map("grD", vim.lsp.buf.declaration, "[G]oto [D]eclaration")
    map("grt", require("telescope.builtin").lsp_type_definitions, "[G]oto [T]ype Definition")
    map("gO", require("telescope.builtin").lsp_document_symbols, "Open Document Symbols")
    map("gW", require("telescope.builtin").lsp_dynamic_workspace_symbols, "Open Workspace Symbols")
  end,
})

-- basic diagnostics configuration
vim.diagnostic.config({
  severity_sort = true,
  float = { border = "rounded", source = "if_many" },
  underline = true,
  virtual_text = {
    source = "if_many",
    spacing = 2,
  },
})

-- lsp server list
local servers = {
  pyright = {}, -- python
  clangd  = {}, -- c++
}

-- ensure tools are installed
require("mason-tool-installer").setup({
  ensure_installed = vim.tbl_keys(servers),
})

require("mason-lspconfig").setup({
  handlers = {
    function(server_name)
      require("lspconfig")[server_name].setup({
        capabilities = capabilities,
      })
    end,
  },
})

-- .