import numpy as np
import soundfile as sf
from pathlib import Path
from core.constants import AppSettings
import noisereduce as nr
import io
import torch


async def to_numpy(wav) -> np.ndarray:
    if hasattr(wav, "numpy"):
        wav = wav.squeeze().cpu().numpy()
    return np.array(wav, dtype=np.float32).ravel()


async def normalise(audio: np.ndarray, peak: float = 0.85) -> np.ndarray:
    m = np.abs(audio).max()
    return audio / m * peak if m > 0 else audio


async def synth_multi(
    model, word: str, lang_code: str, settings: AppSettings
) -> np.ndarray:
    wav = model.generate(
        word, language_id=lang_code, exaggeration=settings.EXAG, cfg_weight=settings.CFG
    )
    return await normalise(await to_numpy(wav))


async def silence(secs: float, sr: int) -> np.ndarray:
    return np.zeros(int(secs * sr), dtype=np.float32)


async def export_wav(audio: np.ndarray, sr: int, path: Path) -> None:
    sf.write(str(path), audio, sr)


async def load_multilingual(device: torch.device):
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    return ChatterboxMultilingualTTS.from_pretrained(device=device)


async def remove_noise_array(audio: np.ndarray, sr: int) -> np.ndarray:
    return nr.reduce_noise(y=audio, sr=sr, stationary=True)


async def audio_to_bytes(audio: np.ndarray, sr: int) -> io.BytesIO:
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format="WAV")
    buf.seek(0)
    return buf


async def build_audio(
    model,
    pairs: list[dict],
    native_lang: str,
    target_lang: str,
    settings: AppSettings,
) -> tuple[np.ndarray, int]:
    sr = model.sr
    native_code = settings.get_lang_code(native_lang.lower())
    target_code = settings.get_lang_code(target_lang.lower())

    segs: list[np.ndarray] = [await silence(settings.SILENCE_LONG_S, sr)]

    for pair in pairs:
        n_audio = await synth_multi(model, pair["native"], native_code, settings)
        segs.append(n_audio)
        segs.append(await silence(settings.SILENCE_SHORT_S, sr))

        t_audio = await synth_multi(model, pair["target"], target_code, settings)
        for _ in range(settings.TARGET_REPETITIONS):
            segs.append(t_audio)
            segs.append(await silence(settings.SILENCE_SHORT_S, sr))

        segs.append(await silence(settings.SILENCE_LONG_S, sr))

    audio = np.concatenate(segs)
    audio = await remove_noise_array(audio, sr)
    return audio, sr
