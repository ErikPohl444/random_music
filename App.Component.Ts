import {Component} from 'angular2/core';
import {Config} from './config.service';
import {Video} from './video';
import {PlaylistComponent} from './playlist.component';

@Component({
    selector: 'my-app',
    templateUrl: 'app/ts/app.component.html',
    directives: [PlaylistComponent]
})

export class AppComponent {
    mainHeading = Config.MAIN_HEADING;
    videos:Array<Video>;

    constructor() {

        this.videos = [
            new Video(1, "The 1975 - Somebody Else", "Bimd2nZirT4", "Calm."),
            new Video(2, "Killswitch Engage - Holy Diver", "NR7dG_m3MsI", "Hell Yeah!")
        ]


    }
}