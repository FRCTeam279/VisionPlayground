import numpy as np
import cv2
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((9*6,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

img = cv2.imread('chess3.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
cv2.imwrite('chess3gray.jpg', gray)
# Find the chess board corners
ret, corners = cv2.findChessboardCorners(gray, (9,6),None)
print(ret)
# If found, add object points, image points (after refining them)
if ret == True:
    objpoints.append(objp)
    
    corners2 = cv2.cornerSubPix(gray,corners,(9,6),(-1,-1),criteria)
    imgpoints.append(corners2)
    
    
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
    
    h,  w = img.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
    
    # undistort
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
    print(str(newcameramtx))
    print(str(mtx))
        
    # crop the image
    # x,y,w,h = roi
    # dst = dst[y:y+h, x:x+w]
    cv2.imwrite('undistort.jpg', dst)
    cv2.waitKey(500)
        


cv2.destroyAllWindows()