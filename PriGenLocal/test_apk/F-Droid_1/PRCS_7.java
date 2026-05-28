/* Application Package Name: org.fdroid.fdroid */
class PRCS_7 {
/**
androidx.work.impl.utils.NetworkApi21;getNetworkCapabilitiesCompat(Landroid/net/ConnectivityManager; Landroid/net/Network;)Landroid/net/NetworkCapabilities;
*/

    public static final android.net.NetworkCapabilities getNetworkCapabilitiesCompat(android.net.ConnectivityManager p1, android.net.Network p2)
    {
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p1, "<this>");
        return p1.getNetworkCapabilities(p2);
    }


}
