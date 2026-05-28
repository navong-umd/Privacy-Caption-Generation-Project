/*Application Package Name: org.fdroid.fdroid
class PRCS_2 {
/**
androidx.core.net.ConnectivityManagerCompat;isActiveNetworkMetered(Landroid/net/ConnectivityManager;)Z
*/

    static boolean isActiveNetworkMetered(android.net.ConnectivityManager p0)
    {
        return p0.isActiveNetworkMetered();
    }

/**
androidx.core.net.ConnectivityManagerCompat;isActiveNetworkMetered(Landroid/net/ConnectivityManager;)Z
*/

    public static boolean isActiveNetworkMetered(android.net.ConnectivityManager p0)
    {
        return androidx.core.net.ConnectivityManagerCompat$Api16Impl.isActiveNetworkMetered(p0);
    }

/**
org.fdroid.fdroid.net.ConnectivityMonitorService;getNetworkState(Landroid/content/Context;)I
*/

    public static int getNetworkState(android.content.Context p7)
    {
        int v7_2 = ((android.net.ConnectivityManager) androidx.core.content.ContextCompat.getSystemService(p7, android.net.ConnectivityManager));
        if (v7_2 != 0) {
            int v1_0 = v7_2.getActiveNetworkInfo();
            if ((v1_0 == 0) && (v7_2.getAllNetworks().length == 0)) {
                String v2_2 = java.net.NetworkInterface.getNetworkInterfaces();
                while (v2_2.hasMoreElements()) {
                    String v3_2 = ((java.net.NetworkInterface) v2_2.nextElement());
                    if ((v3_2.getDisplayName().contains("wlan0")) || ((v3_2.getDisplayName().contains("eth0")) || (v3_2.getDisplayName().contains("ap0")))) {
                        StringBuilder v4_6 = v3_2.getInetAddresses();
                        while (v4_6.hasMoreElements()) {
                            java.net.InetAddress v5_5 = ((java.net.InetAddress) v4_6.nextElement());
                            if (!v5_5.isLoopbackAddress()) {
                                if (!(v5_5 instanceof java.net.Inet6Address)) {
                                    StringBuilder v4_8 = new StringBuilder();
                                    v4_8.append("FLAG_NET_DEVICE_AP_WITHOUT_INTERNET: ");
                                    v4_8.append(v3_2.getDisplayName());
                                    v4_8.append(" ");
                                    v4_8.append(v5_5);
                                    android.util.Log.i("ConnectivityMonitorServ", v4_8.toString());
                                    return 3;
                                } else {
                                }
                            }
                        }
                    }
                }
            }
            if ((v1_0 != 0) && (v1_0.isConnected())) {
                int v0_2 = v1_0.getType();
                if ((v0_2 == 1) || (v0_2 == 9)) {
                    if (!androidx.core.net.ConnectivityManagerCompat.isActiveNetworkMetered(v7_2)) {
                        return 2;
                    } else {
                        return 1;
                    }
                } else {
                    return 1;
                }
            } else {
                return 0;
            }
        } else {
            return 0;
        }
    }


}