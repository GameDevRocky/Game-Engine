from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
import moderngl
import numpy as np
from PyQt6.QtCore import QTimer


class SceneView(QOpenGLWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.ctx = None
        
    def initializeGL(self):
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        # Create a custom FBO
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((self.width(), self.height()), 4)],
            depth_attachment=self.ctx.depth_renderbuffer((self.width(), self.height())),
        )

        # Example geometry: a fullscreen quad
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                out vec2 uv;
                void main() {
                    uv = in_vert * 0.5 + 0.5;
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                in vec2 uv;
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(uv, 0.5, 1.0);
                }
            """
        )

        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def resizeGL(self, w, h):
        if self.ctx:
            self.fbo.release()
            self.fbo = self.ctx.framebuffer(
                color_attachments=[self.ctx.texture((w, h), 4)],
                depth_attachment=self.ctx.depth_renderbuffer((w, h)),
            )

    def paintGL(self):
        self.fbo.use()
        self.ctx.clear(1.0, 0.1, 0.1, 1.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)

        # Render FBO texture back to default framebuffer (optional)
        self.ctx.screen.use()
        self.fbo.color_attachments[0].use(location=0)
        self.ctx.clear(1.0, 0.0, 0.0, 1.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
    
    def update(self):
        pass
    
    