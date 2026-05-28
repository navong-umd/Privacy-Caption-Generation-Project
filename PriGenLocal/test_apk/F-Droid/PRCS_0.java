/*Application Package Name: org.fdroid.fdroid
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

/**
androidx.appcompat.app.TwilightManager;getLastKnownLocation()Landroid/location/Location;
*/

    private android.location.Location getLastKnownLocation()
    {
        android.location.Location v0_1;
        android.location.Location v1_2 = 0;
        if (androidx.core.content.PermissionChecker.checkSelfPermission(this.mContext, "android.permission.ACCESS_COARSE_LOCATION") != 0) {
            v0_1 = 0;
        } else {
            v0_1 = this.getLastKnownLocationForProvider("network");
        }
        if (androidx.core.content.PermissionChecker.checkSelfPermission(this.mContext, "android.permission.ACCESS_FINE_LOCATION") == 0) {
            v1_2 = this.getLastKnownLocationForProvider("gps");
        }
        if ((v1_2 == null) || (v0_1 == null)) {
            if (v1_2 != null) {
                v0_1 = v1_2;
            }
            return v0_1;
        } else {
            if (v1_2.getTime() > v0_1.getTime()) {
                v0_1 = v1_2;
            }
            return v0_1;
        }
    }

/**
androidx.appcompat.app.TwilightManager;isNight()Z
*/

    boolean isNight()
    {
        int v0_0 = this.mTwilightState;
        if (!this.isStateValid()) {
            int v1_4 = this.getLastKnownLocation();
            if (v1_4 == 0) {
                int v0_3;
                android.util.Log.i("TwilightManager", "Could not get last known location. This is probably because the app does not have any location permissions. Falling back to hardcoded sunrise/sunset values.");
                int v0_2 = java.util.Calendar.getInstance().get(11);
                if ((v0_2 >= 6) && (v0_2 < 22)) {
                    v0_3 = 0;
                } else {
                    v0_3 = 1;
                }
                return v0_3;
            } else {
                this.updateState(v1_4);
                return v0_0.isNight;
            }
        } else {
            return v0_0.isNight;
        }
    }


}