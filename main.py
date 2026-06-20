import pygame
import chess
import random
import time
import os
import sys

# --- AYARLAR ---
GENISLIK, YUKSEKLIK = 600, 660
KARE_BOYUTU = GENISLIK // 8
BUTON_YUKSEKLIK = 60
ACIK_RENK = (235, 235, 208)
KOYU_RENK = (119, 148, 85)

IMAGES = {}

# --- DİL SİSTEMİ ---
SECILEN_DIL = "TR"  # Başlangıçta varsayılan, oyuncu seçince güncellenecek

DIL_PAKETI = {
    "TR": {
        "terfi": "Terfi: [V]ezir, [K]ale, [F]il, [A]t",
        "kolay": "KOLAY",
        "orta": "ORTA",
        "zor": "ZOR",
        "mat": "MAT!",
        "berabere": "BERABERE",
        "tekrar": "TEKRAR! BERABERE"
    },
    "EN": {
        "terfi": "Promote: [V]ezir, [K]ale, [F]il, [A]t",
        "kolay": "EASY",
        "orta": "MEDIUM",
        "zor": "HARD",
        "mat": "CHECKMATE!",
        "berabere": "DRAW",
        "tekrar": "3-FOLD! DRAW"
    }
}


# --- NUITKA TEK DOSYA AYARI ---
def kaynak_yolu(goreli_yol):
    """ Nuitka'nın tek dosya (--onefile) modunda resim yollarını doğru bulmasını sağlar """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, goreli_yol)
    return os.path.join(os.path.abspath("."), goreli_yol)


def load_images():
    # Satranç kütüphanesinin ürettiği sembollerle (P, R, N, B, Q, K) birebir eşledik
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for p in pieces:
        try:
            # KLASÖR HATASINI ÖNLEMEK İÇİN: 'imgs/' takısını kaldırdık, direkt ana dizinden okuyor
            dosya_yolu = kaynak_yolu(f"{p}.png")
            IMAGES[p] = pygame.transform.scale(pygame.image.load(dosya_yolu), (KARE_BOYUTU, KARE_BOYUTU))
        except Exception as e:
            print(f"Hata: {dosya_yolu} yüklenemedi! Detay: {e}")


# --- TERFİ SEÇİM EKRANI ---
def terfi_sec(ekran):
    font = pygame.font.SysFont("Arial", 22, bold=True)
    metin = font.render(DIL_PAKETI[SECILEN_DIL]["terfi"], True, (0, 0, 0))

    gosterge_rect = pygame.Rect((GENISLIK // 2) - 175, (YUKSEKLIK // 2) - 40, 350, 80)

    while True:
        pygame.draw.rect(ekran, (255, 255, 255), gosterge_rect, border_radius=8)
        pygame.draw.rect(ekran, (0, 0, 0), gosterge_rect, 3, border_radius=8)
        ekran.blit(metin, (gosterge_rect.x + 25, gosterge_rect.y + 28))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    return chess.QUEEN
                elif event.key == pygame.K_k:
                    return chess.ROOK
                elif event.key == pygame.K_f:
                    return chess.BISHOP
                elif event.key == pygame.K_a:
                    return chess.KNIGHT


# --- OYUN BAŞI DİL SEÇİM MENÜSÜ ---
def dil_secim_ekrani(ekran):
    global SECILEN_DIL
    font = pygame.font.SysFont("Arial", 24, bold=True)

    tr_buton = pygame.Rect((GENISLIK // 2) - 160, (YUKSEKLIK // 2) - 30, 140, 60)
    en_buton = pygame.Rect((GENISLIK // 2) + 20, (YUKSEKLIK // 2) - 30, 140, 60)

    while True:
        ekran.fill((240, 240, 240))

        baslik = font.render("CHOOSE LANGUAGE / DİL SEÇİN", True, (50, 50, 50))
        ekran.blit(baslik, ((GENISLIK // 2) - baslik.get_width() // 2, (YUKSEKLIK // 2) - 100))

        pygame.draw.rect(ekran, (0, 102, 204), tr_buton, border_radius=8)
        pygame.draw.rect(ekran, (204, 0, 0), en_buton, border_radius=8)

        tr_yazi = font.render("TÜRKÇE", True, (255, 255, 255))
        en_yazi = font.render("ENGLISH", True, (255, 255, 255))

        ekran.blit(tr_yazi, (tr_buton.x + (tr_buton.width // 2) - tr_yazi.get_width() // 2, tr_buton.y + 18))
        ekran.blit(en_yazi, (en_buton.x + (en_buton.width // 2) - en_yazi.get_width() // 2, en_buton.y + 18))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if tr_buton.collidepoint(pos):
                    SECILEN_DIL = "TR"
                    return
                elif en_buton.collidepoint(pos):
                    SECILEN_DIL = "EN"
                    return


def main():
    pygame.init()
    ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
    pygame.display.set_caption("Grandmaster Chess v0.1")
    font = pygame.font.SysFont("Arial", 20, bold=True)

    dil_secim_ekrani(ekran)
    load_images()

    tahta = chess.Board()
    secili_kare = None
    gidebilecegi_kareler = []
    zorluk_metni = DIL_PAKETI[SECILEN_DIL]["kolay"]
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                x, y = pos

                if y < BUTON_YUKSEKLIK:
                    if 10 <= x <= 110:
                        zorluk_metni = DIL_PAKETI[SECILEN_DIL]["kolay"]
                    elif 120 <= x <= 220:
                        zorluk_metni = DIL_PAKETI[SECILEN_DIL]["orta"]
                    elif 230 <= x <= 330:
                        zorluk_metni = DIL_PAKETI[SECILEN_DIL]["zor"]

                elif tahta.turn == chess.WHITE and not tahta.is_game_over():
                    col = x // KARE_BOYUTU
                    row = 7 - ((y - BUTON_YUKSEKLIK) // KARE_BOYUTU)
                    if 0 <= row <= 7:
                        t_kare = chess.square(col, row)
                        if secili_kare is None:
                            tas = tahta.piece_at(t_kare)
                            if tas and tas.color == chess.WHITE:
                                secili_kare = t_kare
                                gidebilecegi_kareler = [move.to_square for move in tahta.legal_moves if move.from_square == secili_kare]
                        else:
                            hamle = chess.Move(secili_kare, t_kare)
                            terfi_hamlesi = chess.Move(secili_kare, t_kare, promotion=chess.QUEEN)

                            if terfi_hamlesi in tahta.legal_moves:
                                secilen_tas = terfi_sec(ekran)
                                hamle = chess.Move(secili_kare, t_kare, promotion=secilen_tas)

                            if hamle in tahta.legal_moves:
                                tahta.push(hamle)
                            secili_kare = None
                            gidebilecegi_kareler = []

        if tahta.turn == chess.BLACK and not tahta.is_game_over() and not tahta.can_claim_threefold_repetition():
            pygame.display.flip()
            time.sleep(0.4)

            hamleler = list(tahta.legal_moves)
            if hamleler:
                if zorluk_metni == DIL_PAKETI[SECILEN_DIL]["kolay"]:
                    secilen = random.choice(hamleler)
                elif zorluk_metni == DIL_PAKETI[SECILEN_DIL]["orta"]:
                    can_alicilar = [m for m in hamleler if tahta.is_capture(m)]
                    secilen = random.choice(can_alicilar) if can_alicilar else random.choice(hamleler)
                else:
                    oncelikli = [m for m in hamleler if tahta.is_capture(m) or tahta.gives_check(m)]
                    secilen = random.choice(oncelikli) if oncelikli else random.choice(hamleler)

                tahta.push(secilen)

        ekran.fill((240, 240, 240))

        btn_adlar = [DIL_PAKETI[SECILEN_DIL]["kolay"], DIL_PAKETI[SECILEN_DIL]["orta"], DIL_PAKETI[SECILEN_DIL]["zor"]]
        btn_renkler = [(0, 150, 0), (180, 180, 0), (150, 0, 0)]

        for i, ad in enumerate(btn_adlar):
            x_pos = 10 + i * 110
            if zorluk_metni == ad:
                pygame.draw.rect(ekran, (0, 0, 0), (x_pos - 2, 8, 104, 44), border_radius=5)

            pygame.draw.rect(ekran, btn_renkler[i], (x_pos, 10, 100, 40), border_radius=5)
            txt = font.render(ad, True, (255, 255, 255))
            ekran.blit(txt, (x_pos + 15, 18))

        for r in range(8):
            for c in range(8):
                renk = ACIK_RENK if (r + c) % 2 == 0 else KOYU_RENK
                kare = chess.square(c, 7 - r)
                if secili_kare == kare:
                    renk = (170, 255, 170)
                pygame.draw.rect(ekran, renk,
                                 (c * KARE_BOYUTU, r * KARE_BOYUTU + BUTON_YUKSEKLIK, KARE_BOYUTU, KARE_BOYUTU))

                if kare in gidebilecegi_kareler:
                    merkez_x = c * KARE_BOYUTU + KARE_BOYUTU // 2
                    merkez_y = r * KARE_BOYUTU + BUTON_YUKSEKLIK + KARE_BOYUTU // 2
                    pygame.draw.circle(ekran, (0, 200, 0), (merkez_x, merkez_y), 10)

                tas = tahta.piece_at(kare)
                if tas:
                    p_key = ('w' if tas.color == chess.WHITE else 'b') + tas.symbol().upper()
                    if p_key in IMAGES:
                        ekran.blit(IMAGES[p_key], (c * KARE_BOYUTU, r * KARE_BOYUTU + BUTON_YUKSEKLIK))

        if tahta.is_game_over() or tahta.can_claim_threefold_repetition():
            msg = DIL_PAKETI[SECILEN_DIL]["mat"] if tahta.is_checkmate() else DIL_PAKETI[SECILEN_DIL]["berabere"]
            if tahta.can_claim_threefold_repetition(): msg = DIL_PAKETI[SECILEN_DIL]["tekrar"]

            s_font = pygame.font.SysFont("Arial", 40, bold=True)
            txt_surf = s_font.render(msg, True, (200, 0, 0))
            txt_rect = txt_surf.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2))
            pygame.draw.rect(ekran, (255, 255, 255), txt_rect.inflate(40, 40))
            ekran.blit(txt_surf, txt_rect)

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()