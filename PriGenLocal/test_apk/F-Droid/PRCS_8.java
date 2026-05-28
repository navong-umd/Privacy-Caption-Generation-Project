/*Application Package Name: org.fdroid.fdroid
class PRCS_8 {
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

/**
androidx.work.impl.constraints.trackers.NetworkStateTrackerPre24;readSystemState()Landroidx/work/impl/constraints/NetworkState;
*/

    public androidx.work.impl.constraints.NetworkState readSystemState()
    {
        return androidx.work.impl.constraints.trackers.NetworkStateTrackerKt.getActiveNetworkState(this.connectivityManager);
    }

/**
androidx.work.impl.constraints.trackers.NetworkStateTrackerPre24;readSystemState()Ljava/lang/Object;
*/

    public bridge synthetic Object readSystemState()
    {
        return this.readSystemState();
    }


}