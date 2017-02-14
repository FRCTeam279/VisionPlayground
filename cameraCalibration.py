import numpy as np
import cv2
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

img = cv2.imread('checker1.png')

mtx = np.array([[719.23788899,0,286.30253977],[0,914.46605316,253.07702383],[0,0,1]])
dist = np.array([-.789963891,27.2797236,.0526759913,.0255512576,-338.412991])
h,  w = img.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

# undistort
dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
print(str(newcameramtx))
print(str(mtx))

# crop the image
#x,y,w,h = roi
#dst = dst[y:y+h, x:x+w]
cv2.startWindowThread()
cv2.namedWindow('undistort')
cv2.imshow('undistort', dst)
cv2.imwrite('undistort.jpg', dst)
cv2.waitKey(500)

cv2.destroyAllWindows()
