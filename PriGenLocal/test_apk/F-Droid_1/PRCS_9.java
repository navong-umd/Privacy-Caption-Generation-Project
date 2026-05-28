/* Application Package Name: org.fdroid.fdroid */
class PRCS_9 {
/**
androidx.work.impl.utils.NetworkApi23;getActiveNetworkCompat(Landroid/net/ConnectivityManager;)Landroid/net/Network;
*/

    public static final android.net.Network getActiveNetworkCompat(android.net.ConnectivityManager p1)
    {
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p1, "<this>");
        return p1.getActiveNetwork();
    }


}
