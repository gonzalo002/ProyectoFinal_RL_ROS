import cv2
import numpy as np

cam = cv2.VideoCapture(1)
cam.release()

cam = cv2.VideoCapture(1)
if cam.isOpened():
    _, img = cam.read()
else:
    print('no camera')

# Convertir a escala de grises
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Aplicar un umbral para obtener una imagen binaria
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Desenfoque para eliminar ruido
kernel = np.ones((3, 3), np.uint8)
sure_bg = cv2.dilate(thresh, kernel, iterations=3)

# Aplicar distancia transformada (para obtener áreas "seguras")
dist_transform = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

# Obtener las áreas inciertas
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)

# Etiquetar las regiones de fondo
_, markers = cv2.connectedComponents(sure_fg)

# Añadir 1 para que las marcas de fondo no sean 0
markers = markers + 1
markers[unknown == 255] = 0

# Aplicar Watershed
cv2.watershed(img, markers)

# Colorear los bordes
img[markers == -1] = [0, 0, 255]

# Mostrar el resultado
cv2.imshow("Segmentación Watershed", img)
cv2.waitKey(0)
cv2.destroyAllWindows()