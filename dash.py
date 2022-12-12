import streamlit as st
import cv2
import pyaudio
import time
from math import log10
import audioop  

st.markdown("<h1 style='text-align: center; color: grey;'>Workplace conditions</h1>", unsafe_allow_html=True)

p = pyaudio.PyAudio()
WIDTH = 2
RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
DEVICE = p.get_default_input_device_info()['index']

font = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (250,250)
fontScale = 1
fontColor = (255,0,0)
lineType = 2

def callback(in_data, frame_count, time_info, status):
    global rms
    rms = audioop.rms(in_data, WIDTH) / 32767
    return in_data, pyaudio.paContinue

stream = p.open(format=p.get_format_from_width(WIDTH),
                input_device_index=DEVICE,
                channels=1,
                rate=RATE,
                input=True,
                output=False,
                stream_callback=callback) 

def funct(img):
    #-----Converting image to LAB Color model----------------------------------- 
        lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    #-----Splitting the LAB image to different channels-------------------------
        l, a, b = cv2.split(lab)
    #-----Finding average lightness level in image by fixing some points--------
        y,x,z = img.shape #height, width of image
        #print('>> Image Dimension => X:{}, Y:{}'.format(x,y))
    #Now we will decide some dynamic points on image for checking light intensity
        l_blur = cv2.GaussianBlur(l, (11, 11), 5)
        maxval = []
        count_percent = 3 #percent of total image
        count_percent = count_percent/100
        row_percent = int(count_percent*x) #1% of total pixels widthwise
        column_percent = int(count_percent*y) #1% of total pizel height wise
        for i in range(1,x-1):
            if i%row_percent == 0:
                for j in range(1, y-1):
                    if j%column_percent == 0:
                        pix_cord = (i,j)

                        cv2.circle(img, (int(i), int(j)), 5, (0, 255, 0), 2)
                        img_segment = l_blur[i:i+3, j:j+3]
                        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(img_segment)
                        maxval.append(maxVal)

        avg_maxval = round(sum(maxval) / len(maxval))
        #print('>> Total points: {}'.format(len(maxval)))

        def brightness(avgbr):
            if 0<=avgbr<22:
                avgbr = 0
            elif 22<=avgbr<44:
                avgbr = 1
            elif 44<=avgbr<66:
                avgbr = 2
            elif 66<=avgbr<88:
                avgbr = 3
            elif 88<=avgbr<110:
                avgbr = 4
            elif 110<= avgbr<132:
                avgbr = 5
            elif 132<= avgbr<154:
                avgbr = 6
            elif 154<= avgbr<176:
                avgbr = 7
            elif 176<= avgbr<198:
                avgbr = 8
            elif 198<= avgbr<220:
                avgbr = 9
            else:
                avgbr = 10
            return avgbr

        x = brightness(avg_maxval)
        #return print('>> Average Brightness: {}'.format(x))
        img = cv2.putText(img, format(x), bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        return img
        # print('>> Average Brightness: {}'.format(x))
#st.title("Workplace Conditions")

col1, col2, col3 = st.columns(3)

with col1:
    st.title("Luminosity")
    run = st.checkbox('Run')

    #if __name__ == "__main__":
    if True :
        FRAME_WINDOW = st.image([])
        video_capture = cv2.VideoCapture(0)
        while run:
        # Capturing video
            _, frame = video_capture.read()
            frame_copy = frame.copy()
        # Passing individual frames of video
            canvas = funct(frame)
        # Showing frame returned from classify function
            #cv2.imshow('Video', canvas)
        # Press q to exit webcam
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.imwrite('5.jpg', frame_copy)
                break
        #video_capture.release()
        #cv2.destroyAllWindows()
            FRAME_WINDOW.image(frame)


    #while run:
       #_, frame = video_capture.read()
       #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
       #FRAME_WINDOW.image(frame)
    
with col3:
    st.title("Noise")
    run = st.checkbox('Start')
    WIDTH = 2
    RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
    DEVICE = p.get_default_input_device_info()['index']
    stream = p.open(format=p.get_format_from_width(WIDTH),
                input_device_index=DEVICE,
                channels=1,
                rate=RATE,
                input=True,
                output=False,
                stream_callback=callback) 
    stream.start_stream()

    while run and stream.is_active(): 
        db = 20 * log10(rms) + 120
        #print(f"RMS: {rms} DB: {db}") 
        # refresh every 0.3 seconds 
        time.sleep(0.3)
        if db>20 and db<40:
            st.write(db,'Soft')
        elif db>=40 and db<60:
            st.write(db,'Moderate')
        elif db>=60 and db<80:
            st.write(db,'Loud')
        elif db>=80 and db<110:
            st.write(db,'Very loud')
            st.warning('Consider using hearing protection', icon="⚠️")
        elif db>=110 and db<120:
            st.write(db,'Uncomfortable')
            st.warning('Use hearing protection', icon="⚠️")
        elif db>=120:
            st.write(db,'Painful & Dangerous')
            st.warning('Use hearing protection or AVOID!', icon="⚠️")
    
    stream.stop_stream()
    stream.close()
    p.terminate()

