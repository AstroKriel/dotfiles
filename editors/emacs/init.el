(doom!
 :completion
 company         ;; autocompletion backend
 vertico         ;; modern UI for completion (like Telescope)

 :ui
 doom            ;; Doom's default UI
 modeline        ;; nice statusline
 treemacs        ;; file tree like nvim-tree
 popup           ;; manage transient windows
 hl-todo         ;; highlight TODO/FIXME
 which-key       ;; keybinding hints

 :editor
 evil            ;; Vim emulation
 file-templates  ;; auto-insert snippets
 multiple-cursors ;; <C-n> for multicursor editing
 fold            ;; code folding

 :tools
 lsp             ;; language server protocol
 magit           ;; git porcelain

 :lang
 cc              ;; C, C++
 python          ;; Python + LSP
 sh              ;; Shell scripts
 lua             ;; Lua config/editing

 :config
 (default +bindings +smartparens))
