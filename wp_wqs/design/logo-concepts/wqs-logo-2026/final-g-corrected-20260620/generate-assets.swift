import AppKit
import Foundation

let fileManager = FileManager.default
let outputDirectory = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let sourceURL = URL(fileURLWithPath: CommandLine.arguments[2])

try fileManager.createDirectory(at: outputDirectory, withIntermediateDirectories: true)

guard let sourceIcon = NSImage(contentsOf: sourceURL) else {
    fatalError("Could not load reference icon: \(sourceURL.path)")
}

func pngData(width: Int, height: Int, draw: (NSRect) -> Void) -> Data {
    let image = NSImage(size: NSSize(width: width, height: height))
    image.lockFocusFlipped(true)

    guard let context = NSGraphicsContext.current else {
        fatalError("Could not create graphics context")
    }

    context.imageInterpolation = .high
    context.cgContext.clear(CGRect(x: 0, y: 0, width: width, height: height))
    draw(NSRect(x: 0, y: 0, width: width, height: height))
    image.unlockFocus()

    guard
        let tiff = image.tiffRepresentation,
        let bitmap = NSBitmapImageRep(data: tiff),
        let data = bitmap.representation(using: .png, properties: [:])
    else {
        fatalError("Could not encode PNG")
    }

    return data
}

func writePNG(name: String, width: Int, height: Int, draw: (NSRect) -> Void) throws {
    let data = pngData(width: width, height: height, draw: draw)
    try data.write(to: outputDirectory.appendingPathComponent(name))
}

func drawIcon(in rect: NSRect) {
    sourceIcon.draw(
        in: rect,
        from: NSRect(origin: .zero, size: sourceIcon.size),
        operation: .sourceOver,
        fraction: 1
    )
}

func fittedFont(name: String, fallback: NSFont, size: CGFloat) -> NSFont {
    NSFont(name: name, size: size) ?? fallback
}

func drawHorizontalLogo(width: Int, height: Int) {
    let scale = CGFloat(height) / 600
    let iconRect = NSRect(x: 0, y: 0, width: height, height: height)
    drawIcon(in: iconRect)

    let textX = 650 * scale
    let visibleTop = 118 * scale
    let visibleBottom = 482 * scale
    let chineseFont = fittedFont(
        name: "Songti SC",
        fallback: NSFont.systemFont(ofSize: 205 * scale, weight: .regular),
        size: 205 * scale
    )
    let englishFallback = NSFontManager.shared.convert(
        NSFont.systemFont(ofSize: 82 * scale),
        toHaveTrait: .italicFontMask
    )
    let englishFont = fittedFont(
        name: "Georgia-Italic",
        fallback: englishFallback,
        size: 100 * scale
    )

    let chineseStyle = NSMutableParagraphStyle()
    chineseStyle.alignment = .left
    let chineseAttributes: [NSAttributedString.Key: Any] = [
        .font: chineseFont,
        .foregroundColor: NSColor(calibratedRed: 32 / 255, green: 28 / 255, blue: 24 / 255, alpha: 1),
        .kern: 18 * scale,
        .paragraphStyle: chineseStyle,
    ]
    let englishAttributes: [NSAttributedString.Key: Any] = [
        .font: englishFont,
        .foregroundColor: NSColor(calibratedRed: 81 / 255, green: 74 / 255, blue: 67 / 255, alpha: 1),
        .kern: 2.5 * scale,
    ]

    let chinese = NSAttributedString(string: "王庆松", attributes: chineseAttributes)
    let english = NSAttributedString(string: "Wang Qingsong", attributes: englishAttributes)
    chinese.draw(at: NSPoint(x: textX, y: visibleTop - 62 * scale))

    let englishHeight = english.size().height
    english.draw(at: NSPoint(x: textX + 4 * scale, y: visibleBottom - englishHeight + 4 * scale))
}

let iconSizes = [16, 32, 48, 64, 128, 150, 180, 192, 256, 270, 300, 512, 1024]
for size in iconSizes {
    let destination = outputDirectory.appendingPathComponent("wqs-logo-g-corrected-icon-\(size).png")
    if size == 512 {
        if fileManager.fileExists(atPath: destination.path) {
            try fileManager.removeItem(at: destination)
        }
        try fileManager.copyItem(at: sourceURL, to: destination)
    } else {
        try writePNG(
            name: "wqs-logo-g-corrected-icon-\(size).png",
            width: size,
            height: size
        ) { rect in
            drawIcon(in: rect)
        }
    }
}

let horizontalSizes = [
    (300, 100),
    (600, 200),
    (900, 300),
    (1800, 600),
]
for (width, height) in horizontalSizes {
    try writePNG(
        name: "wqs-logo-g-corrected-\(width)x\(height).png",
        width: width,
        height: height
    ) { _ in
        drawHorizontalLogo(width: width, height: height)
    }
}

try writePNG(
    name: "wqs-logo-g-corrected-preview-white.png",
    width: 1800,
    height: 700
) { rect in
    NSColor.white.setFill()
    rect.fill()
    NSGraphicsContext.current?.cgContext.saveGState()
    NSGraphicsContext.current?.cgContext.translateBy(x: 0, y: 50)
    drawHorizontalLogo(width: 1800, height: 600)
    NSGraphicsContext.current?.cgContext.restoreGState()
}

let sourceData = try Data(contentsOf: sourceURL)
let iconBase64 = sourceData.base64EncodedString()
let iconSVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="Wang Qingsong icon">
  <image href="data:image/png;base64,\(iconBase64)" width="512" height="512"/>
</svg>
"""
try iconSVG.write(
    to: outputDirectory.appendingPathComponent("wqs-logo-g-corrected-icon.svg"),
    atomically: true,
    encoding: .utf8
)

let horizontalURL = outputDirectory.appendingPathComponent("wqs-logo-g-corrected-1800x600.png")
let horizontalBase64 = try Data(contentsOf: horizontalURL).base64EncodedString()
let horizontalSVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="600" viewBox="0 0 1800 600" role="img" aria-label="Wang Qingsong logo">
  <image href="data:image/png;base64,\(horizontalBase64)" width="1800" height="600"/>
</svg>
"""
try horizontalSVG.write(
    to: outputDirectory.appendingPathComponent("wqs-logo-g-corrected-full.svg"),
    atomically: true,
    encoding: .utf8
)
