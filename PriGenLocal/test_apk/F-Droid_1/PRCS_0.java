/* Application Package Name: org.fdroid.fdroid */
class PRCS_0 {
/**
androidx.appcompat.app.TwilightManager;getLastKnownLocationForProvider(Ljava/lang/String;)Landroid/location/Location;
*/

    private android.location.Location getLastKnownLocationForProvider(String p3)
    {
        try {
            if (this.mLocationManager.isProviderEnabled(p3)) {
                return this.mLocationManager.getLastKnownLocation(p3);
            }
        } catch (int v3_2) {
            android.util.Log.d("TwilightManager", "Failed to get last known location", v3_2);
        }
        return 0;
    }


}
