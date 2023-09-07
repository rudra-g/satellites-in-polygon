# 🌌 Satellites in Polygon

Unveil the Mysteries of Satellite Locations within Your Sacred Polygon! 🛰️

(for a no nonsense description look into **"project_overview.txt"** file)

## 🚀 Run Locally

Let's embark on this cosmic journey together. First, summon the project:

```bash
git clone https://link-to-project
```

Step into the cosmic portal:

```bash
cd my-project
```

Now, unleash the magic:

```bash
bash run.sh
```

Or, if you prefer the direct approach:

```bash
./run.sh
```

Feel free to modify the bash file to customize the filepath, or simply invoke the `satellite_processor.py` file directly. The choice is yours!

## 🌟 Overview

**Project Overview**

Prepare to immerse yourself in the celestial realm of satellite data processing. Our mission: to transform cryptic TLE data into mesmerizing satellite coordinates, sifted through the sacred sieve of a user-defined polygon, all wrapped up in a celestial gift for you. Our toolbox includes the enigmatic `sgp4` for satellite conjurations, the mystical `geopandas` for geometric incantations, and the harmonious `multiprocessing` for parallel orchestration.

**How the Project Works**

1. **Coordinate Conversion:** Our odyssey commences with decoding TLE (Two-Line Elements) data—an oracle's scroll containing satellite orbit secrets. Behold the `sgp4` library, our wand to transmute this data into satellite entities, each holding the cosmic coordinates of these celestial travelers at different epochs.

2. **Time Calculation:** We journey into the realms of Julian Dates (JD) and Fractional Days (FR). These mystical artifacts are essential for precise satellite position extraction. We calculate them once, and with the SatrecArray, our code dances through time like a shooting star.

3. **Position Extraction:** Armed with the power of `sgp4`, we summon the ECEF coordinates of satellites for every minute of the day. These coordinates reveal the hidden locations of satellites in the Earth-Centered, Earth-Fixed (ECEF) reference frame. Thanks to the SatrecArray, we conjure all data with a single spell!

4. **Geometric Operations:** We embark on geometric voyages to ascertain if these satellite positions rest within the mystical boundaries of a user's polygon. With the `geopandas` library as our guiding star, we wield the magic of numpy vectorization to determine the celestial truths.

5. **Efficient Filtering:** Our trusted companion `numpy` aids in sifting through data with finesse. We banish rows tainted by the NaN curse, and through geometric sorcery with `geopandas`, we uncover the essence of each satellite's position. Numpy's arrays and vectorized enchantments make explicit loops a thing of the past.

6. **Output Presentation:** The grand finale! We calculate and display the time it takes to complete this celestial quest. We unveil the filtered data, revealing the number of celestial waypoints residing within your enchanted polygon, complete with their celestial coordinates.

**Multiprocessing and Numpy Optimization**

With the power of 8 CPU-workers, we conquer the vast cosmos of 30,000 satellite TLE data in a mere **30 Seconds**. The secrets? Multiprocessing and the magical prowess of Numpy Vector Operations.

- **Multiprocessing**: We summon the spirits of multiprocessing to parallelize our cosmic rituals. By dividing the data into smaller, simultaneous incantations across multiple CPU cores, we reduce the time needed for our mystical computations. This becomes especially potent when confronted with legions of satellites or vast expanses of time.

- **Numpy Vector Operations**: The art of Numpy, a formidable library for numerical sorcery, enhances our data manipulation with elegance. The might of vectorized operations in Numpy empowers us to manipulate vast data arrays without the need for cumbersome loops. This mastery is particularly valuable when filtering data and scrutinizing satellite positions within the mystical polygon, minimizing the burden of computation.

In summary, our project is a symphony of efficiency, orchestrated by the harmonious blend of multiprocessing for parallel might and Numpy for the wizardry of vector operations. With these potent strategies, we stand ready to tackle colossal datasets and intricate geometric enigmas, delivering swift and precise results to you, our honored guest. Prepare to be enchanted by the celestial wonders! 🌟
