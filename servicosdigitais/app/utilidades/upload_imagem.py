# ========================
# Utilidades - salvar/apagar imagem
# ========================
from werkzeug.utils import secure_filename
from flask import current_app
from io import BytesIO
from PIL import Image
import secrets
import time
import os

# Foto_Perfil
ext_uso = {'.jpg', '.jpeg', '.png'}

# nível de compressão WEBP
method=6

# Evita repetir os.path.join em todo lugar
def caminho_imagem(folder: str, filename: str) -> str:
    return os.path.join(current_app.root_path, 'static/fotos_perfil', folder, filename)


def _strip_metadata_and_prepare(img, target_mode=None):
    """
    Remove metadados criando uma nova imagem sem info.
    Se target_mode fornecido, converte antes de criar.
    Retorna Image pronta para salvar.
    """
    if target_mode:
        img = img.convert(target_mode)
    else:
        # criar cópia (Temporária) de segurança
        img = img.copy()

    # Tirar metadata para proteção do usuário;
    base_mode = img.mode
    base = Image.new(base_mode, img.size)
    base.paste(img)
    return base


def salvar_imagem(
    file_storage,
    folder='fotos_perfil',
    prefix=None,
    max_size=(800, 800),
    quality=85,
    gerar_thumb=False,
    thumb_size=(200, 200)
):
    """ Salvar imagem:
    - Limpa, organiza as extensões,
    - Verifica a extensão do arquivo, se não for padrão, será ".jpg";
    - abrir imagem conforme bytes lidos (mais rápido);
    - enviar foto imagem para a pasta correta (fotos_perfil);
    - gerar_thumb -> False (por enquanto até entender);
    - tenta converter  e manter padrão para .webp;
    - se falhar -> salva no formato original;
    - Opicional: tentar salvar em miniatura;
    - se falhar -> salva no formato original;
    -- Retorna: (nome_arquivo, nome_thumb_or_None)
    """

    # leitura segura do stream (para poder reabrir para thumb)
    data = file_storage.read()
    if not data:
        raise ValueError("Arquivo inválido ou vazio.")
    # sempre resetar o cursor do stream para não quebrar usos futuros
    try:
        file_storage.stream.seek(0)
    except Exception:
        pass

    original = secure_filename(file_storage.filename or '')
    _, ext = os.path.splitext(original)
    ext = ext.lower()
    if ext not in ext_uso:
        ext = '.jpg' # padrão caso não seja uma das extensões !mudar!

    # criação de nome único
    hashcode = secrets.token_hex(8)
    ts = int(time.time())
    nome_base = f"{prefix + '_' if prefix else ''}{hashcode}_{ts}"

    # pastas
    pasta = caminho_imagem
    os.makedirs(pasta, exist_ok=True)

    # preparações: abrir imagem principal a partir dos bytes lidos
    bio_main = BytesIO(data)
    img = Image.open(bio_main)
    img.thumbnail(max_size)

    # tentativa de salvar em WEBP
    nome_webp = f"{nome_base}.webp"
    caminho_webp = os.path.join(pasta, nome_webp)
    saved_name = None

    try:
        # preparar imagem para webp: webp aceita RGB ou RGBA
        # remover metadata criando nova imagem
        target_mode = 'RGBA' if img.mode in ('RGBA', 'LA') else 'RGB'
        foto_limpa = _strip_metadata_and_prepare(img, target_mode=target_mode)
        # salvar webp
        foto_limpa.save(caminho_webp, format='WEBP', quality=quality, method=6)
        saved_name = nome_webp
    except Exception:
        nome_padrao = f"{nome_base}{ext}"
        caminho_fallback = os.path.join(pasta, nome_padrao)

        if ext in ('.jpg', '.jpeg'):
            # converter e remover metadata
            foto_limpa = _strip_metadata_and_prepare(img, target_mode='RGB')
            foto_limpa.save(caminho_fallback, format='JPEG', optimize=True, quality=quality)
        else:  # .png
            foto_limpa = _strip_metadata_and_prepare(img, target_mode='RGBA' if img.mode in ('RGBA','LA') else None)
            foto_limpa.save(caminho_fallback, format='PNG', optimize=True)
        saved_name = nome_padrao

    # --- miniatura (opcional) ---
    nome_thumb_ret = None
    if gerar_thumb:
        bio_thumb = BytesIO(data)        # reabrir da melhor qualidade da thumb
        thumb_img = Image.open(bio_thumb)
        thumb_img.thumbnail(thumb_size)

        # tentar salvar thumb em webp também
        nome_webp_thumb = f"{nome_base}_thumb.webp"
        caminho_webp_thumb = os.path.join(pasta, nome_webp_thumb)
        try:
            target_mode = 'RGBA' if thumb_img.mode in ('RGBA', 'LA') else 'RGB'
            thumb_limpa = _strip_metadata_and_prepare(thumb_img, target_mode=target_mode)
            thumb_limpa.save(caminho_webp_thumb, format='WEBP', quality=quality, method=6) # O que é este method: 
            nome_thumb_ret = nome_webp_thumb
        except Exception:
            if saved_name.endswith('.webp'):
                thumb_ext = ext  # usar extensão original
            else:
                thumb_ext = os.path.splitext(saved_name)[1]  #Re-usa a extensão
            nome_thumb = f"{nome_base}_thumb{thumb_ext}"
            caminho_thumb = os.path.join(pasta, nome_thumb)
            if thumb_ext in ('.jpg', '.jpeg'):
                thumb_limpa = _strip_metadata_and_prepare(thumb_img, target_mode='RGB')
                thumb_limpa.save(caminho_thumb, format='JPEG', optimize=True, quality=quality)
            else:
                thumb_limpa = _strip_metadata_and_prepare(thumb_img, target_mode='RGBA' if thumb_img.mode in ('RGBA','LA') else None)
                thumb_limpa.save(caminho_thumb, format='PNG', optimize=True)
            nome_thumb_ret = nome_thumb

    try:
        file_storage.stream.seek(0)
    except Exception:
        pass
    return saved_name, nome_thumb_ret


def apagar_imagem_arquivo(filename, folder='fotos_perfil'):
    """
    Remove arquivo do disco se existir. Não toca no DB.
    Evita remover o arquivo padrão 'default.jpg'.
    Retorna True se apagou, False caso contrário.
    """
    if not filename:
        return False
    if filename == 'default.jpg':
        return False
    caminho = caminho_imagem
    if os.path.exists(caminho):
        try:
            os.remove(caminho)
            return True
        except Exception:
            return False
    return False


def trocar_imagem_usuario(usuario, file_storage, prefix='user'):
    """
    Salva a nova imagem e apaga a antiga (se não for default.jpg).
    Retorna nome_salvo (string) ou None.
    """
    try:
        saved_name, _thumb = salvar_imagem(file_storage, folder='perfil', prefix=f"{prefix}{usuario.id}", gerar_thumb=False)
        # apagar antiga (preservando default.jpg)
        apagar_imagem_arquivo(usuario.foto_perfil, folder='perfil')
        usuario.foto_perfil = saved_name
        return saved_name
    except Exception:
        current_app.logger.exception("Erro ao salvar imagem do usuário")
        return None