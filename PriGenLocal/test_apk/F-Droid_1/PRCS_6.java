/* Application Package Name: org.fdroid.fdroid */
class PRCS_6 {
/**
org.fdroid.fdroid.nearby.BonjourManager;isVpnActive(Landroid/content/Context;)Z
*/

    public static boolean isVpnActive(android.content.Context p1)
    {
        boolean v1_4 = ((android.net.ConnectivityManager) p1.getSystemService("connectivity"));
        boolean v1_5 = v1_4.getNetworkCapabilities(v1_4.getActiveNetwork());
        if (v1_5) {
            return v1_5.hasTransport(4);
        } else {
            return 0;
        }
    }


}
