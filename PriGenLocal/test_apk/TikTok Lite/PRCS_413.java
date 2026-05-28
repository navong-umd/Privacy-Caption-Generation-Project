/*Application Package Name: com.tiktok.lite.go
class PRCS_413 {
/**
X.4Kc;LB()Z
*/

    public static boolean LB()
    {
        int v0_0 = X.4Kc.LBL();
        if (v0_0 == 0) {
            return 0;
        } else {
            int v1 = v0_0.getWifiState();
            if ((v1 == 2) || (v1 == 3)) {
                return 1;
            } else {
                return 0;
            }
        }
    }

/**
X.4Ka;onActivityResumed(Landroid/app/Activity;)V
*/

    public final void onActivityResumed(android.app.Activity p3)
    {
        this.L.unregisterActivityLifecycleCallbacks(this);
        this.LB.invoke(Boolean.valueOf(X.4Kc.LB()));
        return;
    }


}