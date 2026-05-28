/*Application Package Name: com.tiktok.lite.go
class PRCS_404 {
/**
X.4KW;L()Z
*/

    public static boolean L()
    {
        android.location.LocationManager v2_1 = ((android.location.LocationManager) X.4KW.L.getValue());
        if (v2_1 == null) {
            return 0;
        } else {
            if ((v2_1.isProviderEnabled("gps")) || (v2_1.isProviderEnabled("network"))) {
                return 1;
            } else {
                return 0;
            }
        }
    }

/**
X.4KV;onActivityResumed(Landroid/app/Activity;)V
*/

    public final void onActivityResumed(android.app.Activity p3)
    {
        this.L.unregisterActivityLifecycleCallbacks(this);
        this.LB.invoke(Boolean.valueOf(X.4KW.L()));
        return;
    }


}