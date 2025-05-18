import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QGraphicsOpacityEffect, QSizePolicy)
from PyQt6.QtCore import (Qt, QSize, QRect, QPropertyAnimation, QEasingCurve, 
                         QPoint, QPointF)
from PyQt6.QtGui import (QIcon, QPainter, QColor, QBrush, QPen, QPaintEvent, 
                        QLinearGradient, QFont, QRadialGradient)
from utils.resource_utils import resource_path
import webbrowser
import sys
import xml.etree.ElementTree as ET


class AnimatedCircleButton(QPushButton):
    def __init__(self, icon_path, text="", parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.font = QFont("Segoe UI", 10, QFont.Weight.DemiBold)
        self.text = text
        self.icon_path = icon_path  # Store the path instead of loading immediately
        self.icon_size = 60
        self._radius = 45  
        self.hover_radius = 50
        self.base_radius = 45 
        
        # Colors
        self.base_color = QColor(69, 71, 90, 120)
        self.hover_color = QColor(34, 208, 83, 180)
        self.text_color = QColor(220, 220, 220)
        self.highlight_color = QColor(34, 208, 83)
        
        # Animation setup
        self.radius_animation = QPropertyAnimation(self, b"_radius")
        self.radius_animation.setDuration(300)
        self.radius_animation.setEasingCurve(QEasingCurve.Type.OutBack)
        
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
            QToolTip {
                background-color: #2a2b3a;
                color: #ffffff;
                border: 1px solid #22d053;
                padding: 5px;
                border-radius: 3px;
                font: 10pt "Segoe UI";
            }
        """)

    def get_radius(self):
        return self._radius

    def set_radius(self, radius):
        self._radius = radius
        self.update()

    radius = property(get_radius, set_radius)

    def enterEvent(self, event):
        self.radius_animation.stop()
        self.radius_animation.setStartValue(self._radius)
        self.radius_animation.setEndValue(self.hover_radius)
        self.radius_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.radius_animation.stop()
        self.radius_animation.setStartValue(self._radius)
        self.radius_animation.setEndValue(self.base_radius)
        self.radius_animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = QPointF(self.rect().center())
        
        # Draw glow effect when hovered
        if self.underMouse():
            gradient = QRadialGradient(center.x(), center.y(), self.hover_radius + 15)
            gradient.setColorAt(0, QColor(34, 208, 83, 80))
            gradient.setColorAt(1, QColor(34, 208, 83, 0))
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(center, self.hover_radius + 15, self.hover_radius + 15)
        
        # Draw the background circle
        border_width = 2.5 if self.underMouse() else 1.5
        painter.setPen(QPen(self.highlight_color if self.underMouse() else QColor(100, 100, 100, 100), border_width))
        painter.setBrush(QBrush(self.hover_color if self.underMouse() else self.base_color))
        painter.drawEllipse(center, self._radius, self._radius)
        
        # Load icon fresh each time to prevent disappearing
        icon = QIcon(resource_path(f"images/{self.icon_path}"))
        
        # Draw the icon
        icon_rect = QRect(
            int(center.x() - self.icon_size//2),
            int(center.y() - self.icon_size//2),
            self.icon_size,
            self.icon_size
        )
        
        # Always draw icon in normal mode
        icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter, 
                  QIcon.Mode.Normal, QIcon.State.On)
        
        # Draw the text below the circle if provided
        if self.text:
            painter.setFont(self.font)
            text_color = self.highlight_color if self.underMouse() else self.text_color
            painter.setPen(QPen(text_color))
            text_rect = QRect(
                int(center.x() - 50),
                int(center.y() + self._radius + 8),
                100,
                20
            )
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text)

class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1b26, stop:1 #24283b
                );
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)
        
        # Title with decorative elements
        title_container = QHBoxLayout()
        title_container.setContentsMargins(0, 0, 0, 10)
        title_container.setSpacing(15)
        
        # Create icon once and reuse
        help_icon = QIcon(resource_path("images/help_icon.png"))
        icon_pixmap = help_icon.pixmap(QSize(24, 24))
        
        left_decoration = QLabel()
        left_decoration.setPixmap(icon_pixmap)
        
        right_decoration = QLabel()
        right_decoration.setPixmap(icon_pixmap)
        
        title = QLabel("Help & Resources")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font: 24pt "Segoe UI SemiBold";
                color: #e0e0e0;
                padding: 0 15px;
            }
        """)
        
        title_container.addWidget(left_decoration, 0, Qt.AlignmentFlag.AlignVCenter)
        title_container.addStretch(1)
        title_container.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        title_container.addStretch(1)
        title_container.addWidget(right_decoration, 0, Qt.AlignmentFlag.AlignVCenter)
        
        layout.addLayout(title_container)
        
        # Decorative line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("border: 1px solid #22d053; border-radius: 1px;")
        line.setFixedHeight(2)
        layout.addWidget(line)
        
        description = QLabel(
            "Access important resources and support channels with one click. "
            "Get help, report issues, or contribute to the project."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("""
            QLabel {
                font: 11pt "Segoe UI";
                color: #b0b0b0;
                padding: 10px 30px;
            }
        """)
        layout.addWidget(description)
        
        # Button grid layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(20, 10, 20, 20)
        buttons_layout.setSpacing(40)
        
        buttons = [
            ("Report Issue", "bug.png", "https://github.com/ROBOT-RUNNER-COMMUNITY/ROBOT-RUNNER/issues"),
            ("GitHub", "github.png", "https://github.com/ROBOT-RUNNER-COMMUNITY/ROBOT-RUNNER"),
            ("Documentation", "docs.png", "https://robot-runner-doc.readthedocs.io/en/latest/"),
            ("Support", "donate.png", "https://buymeacoffee.com/khabarachre")
        ]
        
        for text, icon, url in buttons:
            btn = AnimatedCircleButton(icon, text)
            btn.setToolTip(f"Open {text} in browser")
            btn.clicked.connect(lambda _, u=url: webbrowser.open(u))
            buttons_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(buttons_layout)

        # Version information
        config_paths = [
            'config.xml',
            os.path.join(os.path.dirname(sys.executable), 'config.xml'),
        ]
                
        config_loaded = False
        for path in config_paths:
            if os.path.exists(path):
                tree = ET.parse(path)
                root = tree.getroot()
                self.version_label = f"{root[0].text}"
                config_loaded = True
                break
                
        if not config_loaded:
            self.version_label = "(Unknown)"

        # Footer with version and copyright
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 20, 0, 0)
        
        version_label = QLabel(f"{self.version_label}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        version_label.setStyleSheet("""
            QLabel {
                font: 9pt "Segoe UI";
                color: #606060;
            }
        """)
        
        copyright_label = QLabel("© ROBOT RUNNER | Developed by Achraf KHABAR")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("""
            QLabel {
                font: 9pt "Segoe UI";
                color: #606060;
            }
        """)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        footer.addWidget(version_label)
        footer.addWidget(copyright_label)
        footer.addWidget(spacer)
        
        layout.addLayout(footer)
        
        self.setLayout(layout)
            
    def setup_animations(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(600)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutBack)

    def showEvent(self, event):
        self.fade_in.start()
        super().showEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Main background with gradient
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(26, 27, 38))
        gradient.setColorAt(1, QColor(36, 40, 59))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(self.rect(), 16, 16)
        
        # Border glow effect
        if self.underMouse():
            border_rect = self.rect().adjusted(1, 1, -1, -1)
            border_gradient = QLinearGradient(0, 0, self.width(), self.height())
            border_gradient.setColorAt(0, QColor(34, 208, 83, 80))
            border_gradient.setColorAt(1, QColor(34, 208, 83, 30))
            
            pen = QPen(QBrush(border_gradient), 2)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(border_rect, 16, 16)
        
        super().paintEvent(event)