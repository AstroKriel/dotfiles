set clipboard=unnamedplus " Use system clipboard for yanks/pastes
set number                " Show absolute line numbers
set relativenumber        " Show relative line numbers
syntax on                 " Enable syntax highlighting
set mouse=a               " Enable mouse (clicks, scroll)
nnoremap <ScrollWheelDown> <Cmd>keepjumps normal! gj<CR>
nnoremap <ScrollWheelUp>   <Cmd>keepjumps normal! gk<CR>