import sys
import pathlib
import chess
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN

# アセットディレクトリ
ASSET_DIR = pathlib.Path(__file__).parent / 'assets'
PIECE_DIR = ASSET_DIR / 'pieces'
BOARD_IMG = ASSET_DIR / 'board.png'
SQUARE_SIZE = 80

# 画像読み込み
def load_images():
    piece_images = {}
    for name in ['wK','wQ','wR','wB','wN','wP','bK','bQ','bR','bB','bN','bP']:
        path = PIECE_DIR / f"{name}.png"
        if path.exists():
            img = pygame.image.load(str(path)).convert_alpha()
            img = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
            piece_images[name] = img
    board_img = pygame.image.load(str(BOARD_IMG)).convert()
    board_img = pygame.transform.smoothscale(board_img, (SQUARE_SIZE*8, SQUARE_SIZE*8))
    return board_img, piece_images

# 画像キー
def piece_key(piece: chess.Piece):
    if piece is None:
        return None
    symbol = piece.symbol()
    color = 'w' if symbol.isupper() else 'b'
    kind = symbol.upper()
    return f"{color}{kind}"

# マウス座標をチェスのマスに変換
def pos_to_square(x, y):
    file = x // SQUARE_SIZE
    rank = 7 - (y // SQUARE_SIZE)
    if 0 <= file <= 7 and 0 <= rank <= 7:
        return chess.square(int(file), int(rank))
    return None

# スタート画面
def start_screen(screen, clock):
    font = pygame.font.SysFont(None, 60)
    title_text = font.render("Chess Game", True, (255, 255, 255))
    start_button = pygame.Rect(220, 300, 200, 80)
    button_color = (0, 200, 0)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    return  # ゲーム開始へ

        screen.fill((0, 0, 50))
        screen.blit(title_text, (200, 150))
        pygame.draw.rect(screen, button_color, start_button)
        btn_text = font.render("Start", True, (255, 255, 255))
        screen.blit(btn_text, (start_button.x + 40, start_button.y + 15))

        pygame.display.flip()
        clock.tick(30)

# 終了画面
def end_screen(screen, clock, result_text):
    font = pygame.font.SysFont(None, 60)
    result_surface = font.render(result_text, True, (255, 255, 255))
    restart_button = pygame.Rect(220, 300, 200, 80)
    button_color = (0, 150, 200)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos):
                    return  # 再スタート

        screen.fill((50, 0, 0))
        screen.blit(result_surface, (100, 150))
        pygame.draw.rect(screen, button_color, restart_button)
        btn_text = font.render("Restart", True, (255, 255, 255))
        screen.blit(btn_text, (restart_button.x + 20, restart_button.y + 15))

        pygame.display.flip()
        clock.tick(30)

# ゲームメイン
def game_loop(screen, clock, board_img, piece_images):
    board = chess.Board()
    selected_sq = None

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return  # メインへ戻って終了
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                sq = pos_to_square(x, y)
                if sq is None:
                    continue
                if selected_sq is None:
                    if board.piece_at(sq) is not None:
                        selected_sq = sq
                else:
                    move = chess.Move(selected_sq, sq)
                    if move in board.legal_moves:
                        board.push(move)
                    else:
                        if chess.Move(selected_sq, sq, promotion=chess.QUEEN) in board.legal_moves:
                            board.push(chess.Move(selected_sq, sq, promotion=chess.QUEEN))
                    selected_sq = None

        # 勝敗判定
        if board.is_game_over():
            if board.is_checkmate():
                if board.turn == chess.WHITE:
                    result_text = "Black Wins!"
                else:
                    result_text = "White Wins!"
            elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
                result_text = "Draw!"
            else:
                result_text = "Game Over"
            end_screen(screen, clock, result_text)
            return  # ゲームループ終了

        # 盤面描画
        screen.blit(board_img, (0, 0))
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece is None:
                continue
            key = piece_key(piece)
            if key in piece_images:
                file = chess.square_file(sq)
                rank = chess.square_rank(sq)
                x = file * SQUARE_SIZE
                y = (7 - rank) * SQUARE_SIZE
                screen.blit(piece_images[key], (x, y))

        if selected_sq is not None:
            file = chess.square_file(selected_sq)
            rank = chess.square_rank(selected_sq)
            rect = pygame.Rect(file * SQUARE_SIZE, (7 - rank) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((255, 255, 0, 80))
            screen.blit(s, rect.topleft)

        pygame.display.flip()
        clock.tick(30)

# メイン関数
def main():
    pygame.init()
    size = (SQUARE_SIZE * 8, SQUARE_SIZE * 8)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Chess (pygame + python-chess)')
    clock = pygame.time.Clock()

    board_img, piece_images = load_images()

    while True:
        start_screen(screen, clock)
        game_loop(screen, clock, board_img, piece_images)

if __name__ == '__main__':
    main()