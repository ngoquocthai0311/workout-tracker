import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { Dialog } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';

@Component({
  selector: 'app-routines',
  imports: [
    Dialog,
    ButtonModule,
    CardModule,
    ScrollPanelModule,
    InputTextModule,
  ],
  templateUrl: './routines.component.html',
  styleUrl: './routines.component.scss',
})
export class RoutinesComponent {
  visible: boolean = false;

  showDialog() {
    this.visible = true;
  }
}
