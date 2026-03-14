import sys
from PySide6.QtCore import (Property, QObject, QPropertyAnimation, Signal, Qt)
from PySide6.QtGui import (QGuiApplication, QMatrix4x4, QQuaternion, QVector3D)
from PySide6.Qt3DCore import (Qt3DCore)
from PySide6.Qt3DExtras import (Qt3DExtras)


class OrbitTransformController(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self._target = None
        self._matrix = QMatrix4x4()
        self._radius = 1
        self._angle = 0

    def setTarget(self, t):
        self._target = t

    def getTarget(self):
        return self._target

    def setRadius(self, radius):
        if self._radius != radius:
            self._radius = radius
            self.updateMatrix()
            self.radiusChanged.emit()

    def getRadius(self):
        return self._radius

    def setAngle(self, angle):
        if self._angle != angle:
            self._angle = angle
            self.updateMatrix()
            self.angleChanged.emit()

    def getAngle(self):
        return self._angle

    def updateMatrix(self):
        self._matrix.setToIdentity()
        self._matrix.rotate(self._angle, QVector3D(0, 1, 0))
        self._matrix.translate(self._radius, 0, 0)
        if self._target is not None:
            self._target.setMatrix(self._matrix)

    angleChanged = Signal()
    radiusChanged = Signal()
    angle = Property(float, getAngle, setAngle, notify=angleChanged)
    radius = Property(float, getRadius, setRadius, notify=radiusChanged)


class Window(Qt3DExtras.Qt3DWindow):
    def __init__(self):
        super().__init__()

        # Camera
        self.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        self.camera().setPosition(QVector3D(0, 0, 40))
        self.camera().setViewCenter(QVector3D(0, 0, 0))

        # For camera controls
        self.createScene()
        self.camController = Qt3DExtras.QOrbitCameraController(self.rootEntity)
        self.camController.setLinearSpeed(50)
        self.camController.setLookSpeed(180)
        self.camController.setCamera(self.camera())

        self.setRootEntity(self.rootEntity)

    def createScene(self):
        # Root entity
        self.rootEntity = Qt3DCore.QEntity()

        # Material
        self.material = Qt3DExtras.QPhongMaterial(self.rootEntity)

        # Cylinder
        self.cylinderEntity = Qt3DCore.QEntity(self.rootEntity)
        self.cylinderMesh = Qt3DExtras.QCylinderMesh()

        self.cylinderMesh.setRadius(5)
        self.cylinderMesh.setRings(100)
        self.cylinderMesh.setSlices(100)
        self.cylinderMesh.setLength(15)

        self.cylinderTransform = Qt3DCore.QTransform()
        self.cylinderTransform.setScale3D(QVector3D(1, 1, 1))
        self.cylinderTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 45))

        self.cylinderEntity.addComponent(self.cylinderMesh)
        self.cylinderEntity.addComponent(self.cylinderTransform)
        self.cylinderEntity.addComponent(self.material)

        # Controller for the cylinder
        self.controller = OrbitTransformController(self.cylinderTransform)
        self.controller.setTarget(self.cylinderTransform)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            current_angle = self.controller.getAngle()
            new_angle = current_angle + 10  # Increment the angle by 10 degrees
            self.controller.setAngle(new_angle)
            self.cylinderTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0.7, 0.5), new_angle))
            self.cylinderEntity.addComponent(self.cylinderTransform)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    view = Window()
    view.show()
    sys.exit(app.exec())
