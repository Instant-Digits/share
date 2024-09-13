from PIL import Image
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster


def PrintLabel(path):
    try:
        im = Image.open(path)    
    except Exception as e:
        print(f"Error loading or resizing image: {e}")
        exit(1)

    backend = 'pyusb'    # 'pyusb', 'linux_kernal', 'network'
    model = 'QL-800'  # Your printer model.
    printer = 'usb://0x04f9:0x209b'  # Replace with the correct USB identifier.
    qlr = BrotherQLRaster(model)
    qlr.exception_on_warning = True
    

    instructions = convert(
        qlr=qlr,
        images=[im],  # List of PIL image objects
        label='62',  # Label size identifier (should match your label)
        rotate='0',  # Rotation angle
        threshold=70.0,  # Black and white threshold in percent
        dither=False,
        compress=False,
        red=False,  # Set to True if using Red/Black 62 mm label tape
        dpi_600=False,
        hq=True,  # High quality
        cut=True
    )
    send(
            instructions=instructions,
            printer_identifier=printer,
            backend_identifier=backend,
            blocking=True
        )
    return {'status': True,'mes': f'Lot number printed'}


# Example usage
if __name__ == "__main__":
    PrintLabel('label.png')