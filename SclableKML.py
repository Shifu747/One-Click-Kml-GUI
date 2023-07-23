import ezdxf
import shapefile
from pyproj import Transformer

def dxf_to_shp(input_file, output_file):
    # Read the DXF file
    doc = ezdxf.readfile(input_file)

    # Create a shapefile writer
    writer = shapefile.Writer(output_file)

    # Define the coordinate system transformation
    transformer = Transformer.from_crs("EPSG:32646", "EPSG:4326", always_xy=True)

    # Create the shapefile fields
    writer.field('Name', 'C')

    # Iterate through each entity in the DXF file
    for entity in doc.modelspace().query('LINE CIRCLE POLYLINE LWPOLYLINE'):
        if entity.dxftype() == 'LINE':
            # Convert LINE entity to shapefile Polyline
            polyline = shapefile.Shape(shapeType=shapefile.POLYLINE)
            polyline.points = [[point[0], point[1]] for point in transformer.itransform([(entity.dxf.start[0], entity.dxf.start[1], 0)])]
            writer.shape(polyline)
            writer.record('Line')
        elif entity.dxftype() == 'CIRCLE':
            # Convert CIRCLE entity to shapefile Point
            point = transformer.itransform([(entity.dxf.center[0], entity.dxf.center[1], 0)])
            writer.point(*point[0])
            writer.record('Circle')
        elif entity.dxftype() in ('POLYLINE', 'LWPOLYLINE'):
            # Convert POLYLINE or LWPOLYLINE entity to shapefile Polyline
            polyline = shapefile.Shape(shapeType=shapefile.POLYLINE)
            polyline.points = [[point[0], point[1]] for point in transformer.itransform([(vertex[0], vertex[1], 0) for vertex in entity.get_points()])]
            writer.shape(polyline)
            writer.record('Polyline')

    # Set the coordinate system for the shapefile
    prj_file = output_file.replace('.shp', '.prj')
    with open(prj_file, 'w') as f:
        f.write('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]')

    # Save the shapefile
    writer.close()

# Usage example
dxf_to_shp('case2.dxf', 'case33.shp')
