/*Application Package Name: org.fdroid.fdroid
class PRCS_3 {
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
androidx.work.impl.constraints.trackers.NetworkStateTrackerKt;getActiveNetworkState(Landroid/net/ConnectivityManager;)Landroidx/work/impl/constraints/NetworkState;
*/

    public static final androidx.work.impl.constraints.NetworkState getActiveNetworkState(android.net.ConnectivityManager p5)
    {
        int v3_0;
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p5, "<this>");
        androidx.work.impl.constraints.NetworkState v0_4 = p5.getActiveNetworkInfo();
        int v1 = 0;
        if ((v0_4 == null) || (!v0_4.isConnected())) {
            v3_0 = 0;
        } else {
            v3_0 = 1;
        }
        boolean v4 = androidx.work.impl.constraints.trackers.NetworkStateTrackerKt.isActiveNetworkValidated(p5);
        boolean v5_1 = androidx.core.net.ConnectivityManagerCompat.isActiveNetworkMetered(p5);
        if ((v0_4 != null) && (!v0_4.isRoaming())) {
            v1 = 1;
        }
        return new androidx.work.impl.constraints.NetworkState(v3_0, v4, v5_1, v1);
    }


}