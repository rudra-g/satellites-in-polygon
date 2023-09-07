import datetime
import numpy as np
from shapely.geometry import Polygon, Point
from sgp4.api import Satrec
from sgp4.api import jday
import multiprocessing
from multiprocessing import cpu_count
from sgp4.api import SatrecArray
import geopandas as gpd
import pyproj
from sgp4.api import SGP4_ERRORS
import time

def ecef2lla(i, pos_x, pos_y, pos_z):
    """
    PROVIDED FUNCTION - (Not changed)
    Converts ECEF (Earth-Centered, Earth-Fixed) coordinates to LLA (Longitude, Latitude, Altitude) coordinates.

    Args:
        i (int): Index of the position.
        pos_x (numpy.ndarray): X-coordinates of positions.
        pos_y (numpy.ndarray): Y-coordinates of positions.
        pos_z (numpy.ndarray): Z-coordinates of positions.

    Returns:
        tuple: A tuple containing the Longitude, Latitude, and Altitude.
    """
    ecef = pyproj.Proj(proj="geocent", ellps="WGS84", datum="WGS84")
    lla = pyproj.Proj(proj="latlong", ellps="WGS84", datum="WGS84")
    lona, lata, alta = pyproj.transform(
        ecef, lla, pos_x[i], pos_y[i], pos_z[i], radians=False
    )
    return lona, lata, alta

def create_satellites(tle_data):
    """
    Create satellite objects from TLE (Two-Line Elements) data.

    Args:
        tle_data (list): A list containing TLE data.

    Returns:
        Satrec: A satellite object.
    """
    if len(tle_data) != 3:
        return None
    s = tle_data[1]
    t = tle_data[2]
    return Satrec.twoline2rv(s, t)


def create_SatrecArray_of_satellites(sat_data):
    """
    Create a SatrecArray from a list of satellite objects.

    Args:
        sat_data (list): A list of satellite objects.

    Returns:
        SatrecArray: A SatrecArray containing satellite objects.
    """
    sats = SatrecArray(sat_data)
    return sats


def build_jd_and_fr_lists_for_day(year, month, day):
    """
    Build Julian Date (JD) and Fractional Day (FR) lists for a given date with one minute interval.

    Args:
        year (int): Year.
        month (int): Month.
        day (int): Day.

    Returns:
        numpy.ndarray: Arrays containing JD and FR values for each minute of the day.
    """
    num_minutes = 24 * 60
    minutes = list(range(num_minutes))
    #creates jd and fr for an entire day with 1 minute intervals
    jd_list, fr_list = zip(
        *[jday(year, month, day, minute // 60, minute % 60, 0) for minute in minutes]
    )
    return np.array(jd_list), np.array(fr_list)


def get_positional_data_from_satellites(jd_chunk, fr_chunk, sat_array):
    """
    Get positional data (ECEF coordinates) from satellite objects.

    Args:
        jd_chunk (numpy.ndarray): Array of Julian Dates.
        fr_chunk (numpy.ndarray): Array of Fractional Days.
        sat_array (SatrecArray): SatrecArray containing satellite objects.

    Returns:
        numpy.ndarray: Array containing positional data.
    """
    e, r, v = sat_array.sgp4(jd_chunk, fr_chunk)
    flattened_out_error_codes = set(e.ravel())
    if any(flattened_out_error_codes):
        print("the following errors were caught during data extraction -")
        [print(SGP4_ERRORS[index]) for index in flattened_out_error_codes if index!=0]
    return r.reshape(-1, r.shape[-1])


def are_points_inside_polygon(point_coords, gdf_polygon):
    """
    Check if points are inside a polygon.

    Args:
        point_coords (list): List of point coordinates.
        gdf_polygon (geopandas.geodataframe.GeoDataFrame): GeoDataFrame containing the polygon.

    Returns:
        numpy.ndarray: Boolean array indicating whether each point is inside the polygon.
    """

    #using geopandas as it is optimised to be used with numpy
    gseries_points = gpd.GeoSeries([Point(coords) for coords in point_coords])
    is_inside = gseries_points.within(gdf_polygon["geometry"][0])
    return is_inside


def filter_rows_in_usable_data(input_array, gdf_polygon):
    """
    Filter rows in the input array based on whether points are inside the polygon.

    Args:
        input_array (numpy.ndarray): Input array containing data.
        gdf_polygon (geopandas.geodataframe.GeoDataFrame): GeoDataFrame containing the polygon.

    Returns:
        numpy.ndarray: Filtered array.
    """

    #removing rows with nan elements
    nan_rows = np.isnan(input_array).any(axis=1)
    input_array = input_array[~nan_rows]
    is_inside = are_points_inside_polygon(input_array[:, :2], gdf_polygon)
    result_array = input_array[is_inside]
    return result_array


def get_ecef2lla_data_from_chunks(args):
    """
    Convert ECEF coordinates to LLA coordinates for data chunks if they are within user provided polygon.

    Args:
        args (tuple): Tuple containing positional data and GeoDataFrame polygon.

    Returns:
        numpy.ndarray: Converted LLA data.
    """
    #arguments are passed through args to be better suitable for multiprocessing
    positional_data, gdf_polygon = args
    column0 = list(range(len(positional_data)))
    lona, lata, alta = ecef2lla(
        column0, positional_data[:, 0], positional_data[:, 1], positional_data[:, 2]
    )
    usable_data_array = np.column_stack((lona, lata, alta))
    filtered_usable_data_array = filter_rows_in_usable_data(
        usable_data_array, gdf_polygon
    )
    return filtered_usable_data_array


def read_lines(filename):
    """
    Read lines from a file and return them as a list of strings.

    Args:
        filename (str): Name of the file to read.

    Returns:
        list: List of lines read from the file.
    """
    lines = []
    with open(filename, "r") as file:
        lines = [line.strip() for line in file]
    return lines


def get_date_from_input():
    """
    Get a date in YYYY-MM-DD format from user input.

    Returns:
        tuple: Year, month, and day extracted from the input date.
    """
    while True:
        date_str = input("Enter a date in YYYY-MM-DD format: ")
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day
            return year, month, day
        except ValueError:
            print("Invalid date format. Please enter a date in YYYY-MM-DD format.")


def get_latitude_longitude_pairs():
    """
    Get latitude and longitude pairs from user input.

    Returns:
        list: List of latitude and longitude pairs.
    """
    latitude_longitude_pairs = []
    for i in range(1, 5):
        while True:
            try:
                pair_str = input(f"Enter latitude longitude pair {i} (e.g., 1.1 2.2): ")
                lat, lon = map(float, pair_str.split())
                latitude_longitude_pairs.append([lat, lon])
                break
            except ValueError:
                print(
                    "Invalid input. Please enter two floating-point numbers separated by a space."
                )
    return latitude_longitude_pairs


def create_polygon_from_user_input():
    """
    Create a GeoDataFrame polygon from user input.

    Returns:
        geopandas.geodataframe.GeoDataFrame: A GeoDataFrame containing the created polygon.
    """
    number_pairs = get_latitude_longitude_pairs()
    shapely_polygon = Polygon(number_pairs)
    gdf_polygon = gpd.GeoDataFrame({"geometry": [shapely_polygon]})
    return gdf_polygon


def get_positional_data_from_tle(lines,year, month, day):
    """
    Get positional data (ECEF coordinates) from TLE data for one day.

    Args:
        lines (list): List of TLE data lines.
        year (int): Year.
        month (int): Month.
        day (int): Day.
        
    Returns:
        numpy.ndarray: Array containing positional data.
    """
    #from 3 line chunks creating satellite objects
    sat_data = [create_satellites(lines[l : l + 3]) for l in range(0, len(lines), 3)]
    #creating list of jd and fr for an entire day with one minute intervals
    jd, fr = build_jd_and_fr_lists_for_day(year, month, day)
    #create a SatrecArray from satellites for faster extraction
    sat_array = create_SatrecArray_of_satellites(sat_data)
    #extract positional data from SatrecArray
    positional_data = get_positional_data_from_satellites(jd, fr, sat_array)
    return positional_data


def get_filtered_result_from_positional_data(positional_data, gdf_polygon):
    """
    Get filtered results from positional data based on a polygon.

    Args:
        positional_data (numpy.ndarray): Array containing positional data.
        gdf_polygon (geopandas.geodataframe.GeoDataFrame): GeoDataFrame containing the polygon.

    Returns:
        numpy.ndarray: Filtered array.
    """
    #finding out the optimal chunk size based on the cpu_count
    chunk_size = len(positional_data) // cpu_count()

    #creating arguments for each chunk
    data_chunks = [
        (positional_data[i : i + chunk_size], gdf_polygon)
        for i in range(0, len(positional_data), chunk_size)
    ]

    #processing each chunk with multiprocessing.Pool() which returns filtered data
    with multiprocessing.Pool() as pool:
        processed_chunks = pool.map(get_ecef2lla_data_from_chunks, data_chunks)

    #combines the result of processed chunks and returns it
    return np.vstack(processed_chunks)



def process_satellite_data_for_filepath(file_path):
    """
    Process satellite data from a given file path and filter it based on a user-defined polygon.

    Args:
        file_path (str): The path to the file containing TLE data for multiple satellites.

    Returns:
        None
    """
    # Get the user-defined date in YYYY-MM-DD format
    year, month, day = get_date_from_input()
    # Create a GeoDataFrame polygon based on user input
    gdf_polygon = create_polygon_from_user_input()
    # Record the start time for performance measurement
    start = time.time()
    # Read TLE data from the specified file
    lines = read_lines(file_path)
    # Get positional data (ECEF coordinates) for satellites on the specified date
    positional_data = get_positional_data_from_tle(lines, year, month, day)
    # Filter the positional data based on the user-defined polygon
    result = get_filtered_result_from_positional_data(positional_data, gdf_polygon)
    # Calculate and print the time taken for processing
    print(f"{(time.time() - start)} - Seconds taken")

    if result.size > 0:
        # If there is filtered data, print the number of data points and the data itself
        print(f"Number of filtered data - {len(result)}")
        print(result)
    else:
        # If no data is found inside the polygon, print a message
        print("No data found")
