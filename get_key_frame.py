import os
import sys
import cv2
import subprocess

filename = '/usr/local/google/home/judeyou/PycharmProjects/m3u8downloader/temp/ads/master_360_00691.ts'


def get_frame_types(video_fn):
    command = 'ffprobe -v error -show_entries frame=pict_type -of default=noprint_wrappers=1'.split()
    out = subprocess.check_output(command + [video_fn]).decode()
    frame_types = out.replace('pict_type=','').split()
    return zip(range(len(frame_types)), frame_types)

def save_i_keyframes(video_fn):
    frame_types = get_frame_types(video_fn)
    i_frames = [x[0] for x in frame_types if x[1]=='I']
    if i_frames:
        basename = os.path.splitext(os.path.basename(video_fn))[0]
        cap = cv2.VideoCapture(video_fn)
        for frame_no in i_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            outname = basename+'_i_frame_'+str(frame_no)+'.jpg'
            cv2.imwrite(outname, frame)
            print ('Saved: '+outname)
        cap.release()
    else:
        print ('No I-frames in '+video_fn)


def get_i_keyframes(video_fn):
    result = []
    frame_types = get_frame_types(video_fn)
    i_frames = [x[0] for x in frame_types if x[1]=='I']
    if i_frames:
        basename = os.path.splitext(os.path.basename(video_fn))[0]
        cap = cv2.VideoCapture(video_fn)
        for frame_no in i_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            outname = basename+'_i_frame_'+str(frame_no)+'.jpg'
            outname = 'tmp/' + outname
            cv2.imwrite(outname, frame)
            result.append([outname, frame])
            # print ('extract: ' + outname)
        cap.release()
    else:
        print ('No I-frames in '+video_fn)
    return result


def list_all(path):
    for dirpath, dirnames, filenames in os.walk(path):
        print dirpath, dirnames, filenames, '\n'
        for filename in filenames:
            print dirpath+filename
            save_i_keyframes(dirpath + '/' + filename)


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        # save_i_keyframes(args[1])
        list_all(args[1])
    else:
        print 'Fail, params error, try:'
        print 'python', args[0], 'dir_your_ts_path', '\n'

