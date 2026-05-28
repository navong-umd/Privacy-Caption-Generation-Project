/*Application Package Name: org.fdroid.fdroid
class PRCS_24 {
/**
androidx.work.impl.utils.NetworkApi23;getActiveNetworkCompat(Landroid/net/ConnectivityManager;)Landroid/net/Network;
*/

    public static final android.net.Network getActiveNetworkCompat(android.net.ConnectivityManager p1)
    {
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p1, "<this>");
        return p1.getActiveNetwork();
    }

/**
androidx.work.impl.constraints.trackers.NetworkStateTrackerKt;isActiveNetworkValidated(Landroid/net/ConnectivityManager;)Z
*/

    public static final boolean isActiveNetworkValidated(android.net.ConnectivityManager p4)
    {
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p4, "<this>");
        boolean v0_1 = 0;
        try {
            SecurityException v4_1 = androidx.work.impl.utils.NetworkApi21.getNetworkCapabilitiesCompat(p4, androidx.work.impl.utils.NetworkApi23.getActiveNetworkCompat(p4));
        } catch (SecurityException v4_2) {
            androidx.work.Logger.get().error(androidx.work.impl.constraints.trackers.NetworkStateTrackerKt.TAG, "Unable to validate active network", v4_2);
            return v0_1;
        }
        if (v4_1 == null) {
            return v0_1;
        } else {
            v0_1 = androidx.work.impl.utils.NetworkApi21.hasCapabilityCompat(v4_1, 16);
            return v0_1;
        }
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