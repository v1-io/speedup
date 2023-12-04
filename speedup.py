import argparse
import os
import librosa
import soundfile as sf
from tqdm import tqdm
from multiprocessing import Pool
from pydub import AudioSegment

def change_speed(input_file, output_file, speed=1.5):
    y, sr = librosa.load(input_file, sr=None)
    y_fast = librosa.effects.time_stretch(y, rate=speed)
    
    # Temporary WAV file path
    temp_output = output_file.replace('.mp3', '.wav')
    
    # Save as WAV first
    sf.write(temp_output, y_fast, sr)

    # Convert WAV to MP3 using pydub
    sound = AudioSegment.from_wav(temp_output)
    sound.export(output_file, format="mp3")

    # Remove temporary WAV file
    os.remove(temp_output)

def process_file(args):
    file_path, output_directory, speed = args
    filename = os.path.basename(file_path)
    new_file_path = os.path.join(output_directory, os.path.splitext(filename)[0] + "_speedup.mp3")
    change_speed(file_path, new_file_path, speed)
    return file_path

def process_directory(input_directory, output_directory, speed, num_processes=1):
    files = [(os.path.join(input_directory, f), output_directory, speed) 
             for f in os.listdir(input_directory) if f.endswith('.mp3')]
    
    with Pool(num_processes) as pool:
        processed_files = list(tqdm(pool.imap(process_file, files), total=len(files)))
    
    return processed_files

def main():
    parser = argparse.ArgumentParser(description="Change speed of MP3 files without changing pitch")
    parser.add_argument("path", help="Path to the MP3 file or directory")
    parser.add_argument("-s", "--speed", type=float, default=1.5, help="Speed multiplier (default: 1.5)")
    parser.add_argument("-o", "--output", help="Output directory", default=None)
    args = parser.parse_args()

    output_directory = args.output if args.output else os.path.dirname(os.path.abspath(args.path))
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    if os.path.isdir(args.path):
        processed_files = process_directory(args.path, output_directory, args.speed)
    elif os.path.isfile(args.path) and args.path.endswith('.mp3'):
        processed_files = [process_file((args.path, output_directory, args.speed))]
    else:
        print("Invalid path or file format. Please provide a valid MP3 file or directory.")
        return
    
if __name__ == "__main__":
    main()
