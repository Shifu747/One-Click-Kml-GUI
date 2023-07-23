import ezdxf
import simplekml
from pyproj import Transformer

def dxf_to_kml(input_file, output_file):
    # Read the DXF file
    doc = ezdxf.readfile(input_file)

    # Create a KML object
    kml = simplekml.Kml()

    # Define the coordinate system transformation
    transformer = Transformer.from_crs("EPSG:32646", "EPSG:4326", always_xy=True)

    # Iterate through each entity in the DXF file
    for entity in doc.modelspace().query('LINE CIRCLE POLYLINE LWPOLYLINE'):
        if entity.dxftype() == 'LINE':
            # Convert LINE entity to KML LineString
            line = kml.newlinestring(name='Line')
            line.coords = [(point[0], point[1], 0) for point in transformer.itransform([(entity.dxf.start[0], entity.dxf.start[1], 0)])]
            line.altitudemode = simplekml.AltitudeMode.relativetoground
        elif entity.dxftype() == 'CIRCLE':
            # Convert CIRCLE entity to KML Point
            circle = kml.newpoint(name='Circle')
            circle.coords = [(point[0], point[1], 0) for point in transformer.itransform([(entity.dxf.center[0], entity.dxf.center[1], 0)])]
            circle.altitudemode = simplekml.AltitudeMode.relativetoground
        elif entity.dxftype() in ('POLYLINE', 'LWPOLYLINE'):
            # Convert POLYLINE or LWPOLYLINE entity to KML LineString
            polyline = kml.newlinestring(name='Polyline')
            polyline.coords = [(point[0], point[1], 0) for point in transformer.itransform([(vertex[0], vertex[1], 0) for vertex in entity.get_points()])]
            polyline.altitudemode = simplekml.AltitudeMode.relativetoground

    # Save the KML file
    kml.save(output_file)

# Usage example
dxf_to_kml('case2.dxf', 'case.kml')
